import datetime
import re
from collections import Counter
from typing import List

from src.business_object.conversation import Conversation
from src.business_object.echange import Echange
from src.dao.db_connection import DBConnection
from src.dao.prompt_dao import PromptDAO


class ConversationDAO:
    @staticmethod
    def creer_conversation(
        conversation: Conversation, proprietaire_id: int | None = None
    ) -> Conversation:
        """
        Crée une nouvelle conversation en base de données.

        Parameters
        ----------
        conversation : Conversation
            L'objet Conversation contenant au minimum un nom.
        proprietaire_id : int | None, optional
            L'identifiant du créateur à ajouter aux participants, by default None.

        Returns
        -------
        Conversation
            La conversation mise à jour avec son `id`, sa date de création et son `prompt_id`.

        Raises
        ------
        ValueError
            Si le titre est vide ou si la personnalisation (prompt) est invalide.
        """
        titre = (conversation.nom or "").strip()
        if not titre:
            raise ValueError("Le nom (titre) de la conversation est obligatoire.")

        # Resolve prompt_id :
        perso = conversation.personnalisation
        prompt_id = None
        if isinstance(perso, str):
            perso = perso.strip()
            if perso:
                pid = PromptDAO.get_id_by_name(perso)
                if pid is None:
                    raise ValueError(f"Prompt inconnu : '{perso}'")
                prompt_id = pid
        elif isinstance(perso, int):
            if not PromptDAO.exists_id(perso):
                raise ValueError(f"prompt_id inexistant: {perso}")
            prompt_id = perso

        with DBConnection().connection as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO conversations (titre, prompt_id)
                    VALUES (%(titre)s, %(prompt_id)s)
                    RETURNING id, cree_le;
                    """,
                    {"titre": titre, "prompt_id": prompt_id},
                )
                row = cur.fetchone()
                conversation.id = row["id"]
                conversation.date_creation = row["cree_le"]
                conversation.personnalisation = prompt_id

                if proprietaire_id is not None:
                    cur.execute(
                        """
                        INSERT INTO conversations_participants (conversation_id, utilisateur_id)
                        VALUES (%(cid)s, %(uid)s)
                        ON CONFLICT DO NOTHING;
                        """,
                        {"cid": conversation.id, "uid": proprietaire_id},
                    )

        return conversation

    @staticmethod
    def trouver_par_id(id_conv: int) -> Conversation:
        """
        Récupère une conversation dans la base à partir de son identifiant.

        Parameters
        ----------
        id_conv : int
            Identifiant de la conversation.

        Returns
        -------
        Conversation
            L'objet Conversation correspondant.

        Raises
        ------
        Exception
            Si aucune conversation ne correspond à cet ID.
        """
        with DBConnection().connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, titre, prompt_id, cree_le
                    FROM conversations
                    WHERE id = %(id_conv)s;
                    """,
                    {"id_conv": id_conv},
                )
                conv = cursor.fetchone()
        if not conv:
            raise Exception(f"Aucune conversation trouvée avec id={id_conv}")
        return Conversation(
            id=conv["id"],
            nom=conv["titre"],
            personnalisation=conv["prompt_id"],
            date_creation=conv["cree_le"],
        )

    @staticmethod
    def renommer_conv(id_conv: int, nouveau_nom: str):
        """
        Renomme une conversation dans la base de données.

        Parameters
        ----------
        id_conv : int
            Identifiant de la conversation à renommer.
        nouveau_nom : str
            Nouveau nom de la conversation.

        Returns
        -------
        str
            Message confirmant le succès.

        Raises
        ------
        Exception
            Si l'id est invalide ou si la modification échoue.
        """
        if not isinstance(id_conv, int):
            raise Exception(f"l'id {id_conv} est invalide et doit être un entier naturel")
        with DBConnection().connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE conversations                          
                    SET titre = %(nouveau_nom)s                   
                    WHERE id = %(id_conv)s;
                    """,
                    {"nouveau_nom": nouveau_nom, "id_conv": id_conv},
                )
                count = cursor.rowcount
        if count > 0:
            return "titre modifié avec succès"
        else:
            raise Exception(f"Erreur dans la modification du titre pour id_conv = {id_conv}")

    @staticmethod
    def supprimer_conv(id_conv: int) -> str:
        """
        Supprime une conversation de la base.

        Parameters
        ----------
        id_conv : int
            Identifiant de la conversation à supprimer.

        Returns
        -------
        str
            Message confirmant la suppression.

        Raises
        ------
        Exception
            Si l'id est invalide ou si aucune conversation n'a été supprimée.
        """
        if not isinstance(id_conv, int):
            raise Exception(f"l'id {id_conv} est invalide et doit être un entier naturel")
        with DBConnection().connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                DELETE FROM conversations
                WHERE id = %(id_conv)s
                """,
                    {"id_conv": id_conv},
                )
            count = cursor.rowcount
        if count > 0:
            return f"la conversation d'id={id_conv} a bien été supprimée"
        else:
            raise Exception(f"echec de la suppression de la conversation d'identifiant {id_conv}")

    @staticmethod
    def lister_conversations(id_user: int, n=None) -> list[Conversation]:
        """
        Liste les conversations auxquelles un utilisateur participe,
        triées par date du dernier message.

        Parameters
        ----------
        id_user : int
            Identifiant de l'utilisateur.
        n : int | None, optional
            Nombre maximum de conversations à retourner.

        Returns
        -------
        list[Conversation]
            Liste des conversations trouvées.
        """
        query = """

            SELECT c.*, MAX(m.cree_le) AS dernier_message
            FROM conversations c
            JOIN conversations_participants uc ON c.id = uc.conversation_id
            LEFT JOIN messages m ON c.id = m.conversation_id
            WHERE uc.utilisateur_id = %(id_user)s
            GROUP BY c.id
            ORDER BY dernier_message DESC NULLS LAST
        """

        params = {"id_user": id_user}
        if n and n > 0:
            query += " LIMIT %(n)s"
            params["n"] = n

        with DBConnection().connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall() or []
        return [
            Conversation(
                id=row["id"],
                nom=row["titre"],
                personnalisation=row["prompt_id"],
                date_creation=row["cree_le"],
            )
            for row in rows
        ]

    @staticmethod
    def rechercher_mot_clef(id_user: int, mot_clef: str) -> list[Conversation]:
        """
        Recherche les conversations d'un utilisateur contenant un mot-clé dans
        leur titre ou dans un message.

        Parameters
        ----------
        id_user : int
            Identifiant de l'utilisateur.
        mot_clef : str
            Mot-clé recherché.

        Returns
        -------
        list[Conversation]
            Conversations contenant le mot-clé.

        Raises
        ------
        None
            Une liste vide est retournée si aucun résultat.
        """
        if not isinstance(mot_clef, str) or not mot_clef.strip():
            return []
        pattern = f"%{mot_clef.strip()}%"
        with DBConnection().connection as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT DISTINCT c.id, c.titre, c.prompt_id, c.cree_le
                    FROM conversations c
                    JOIN conversations_participants cp
                        ON cp.conversation_id = c.id
                    LEFT JOIN messages m
                        ON m.conversation_id = c.id
                    WHERE cp.utilisateur_id = %(uid)s
                      AND (
                            c.titre ILIKE %(pattern)s
                         OR m.contenu ILIKE %(pattern)s
                      )
                    ORDER BY c.cree_le DESC;
                    """,
                    {"uid": id_user, "pattern": pattern},
                )
                rows = cur.fetchall()
        return [
            Conversation(
                id=r["id"],
                nom=r["titre"],
                personnalisation=r["prompt_id"],
                date_creation=r["cree_le"],
            )
            for r in rows
        ]

    @staticmethod
    def rechercher_date(id_user: int, date: datetime.date) -> list[Conversation]:
        """
        Recherche les conversations contenant au moins un message envoyé à une date donnée.

        Parameters
        ----------
        id_user : int
            Identifiant de l'utilisateur.
        date : datetime.date
            La date recherchée.

        Returns
        -------
        list[Conversation]
            Conversations contenant un message ce jour-là.

        Raises
        ------
        Exception
            Si le format de la date est invalide.
        """
        # Normalisation du paramètre "date" en début/fin de journée
        if isinstance(date, datetime.date) and not isinstance(date, datetime.datetime):
            d0 = datetime.datetime(date.year, date.month, date.day)
        elif isinstance(date, datetime.datetime):
            d0 = datetime.datetime(date.year, date.month, date.day)
        else:
            raise Exception(f"la date {date!r} n'est pas au format datetime/date")

        d1 = d0 + datetime.timedelta(days=1)

        sql = """
            SELECT DISTINCT c.id, c.titre, c.prompt_id, c.cree_le
            FROM conversations c
            JOIN conversations_participants cp
            ON cp.conversation_id = c.id
            JOIN messages m
            ON m.conversation_id = c.id
            WHERE cp.utilisateur_id = %(uid)s
            AND m.cree_le >= %(start)s
            AND m.cree_le <  %(end)s
            ORDER BY c.cree_le DESC;
        """

        with DBConnection().connection as conn:
            with conn.cursor() as cur:
                cur.execute(sql, {"uid": id_user, "start": d0, "end": d1})
                rows = cur.fetchall() or []

        return [
            Conversation(
                id=r["id"],
                nom=r["titre"],
                personnalisation=r["prompt_id"],
                date_creation=r["cree_le"],
            )
            for r in rows
        ]

    def rechercher_conv_mot_et_date(id_user: int, mot_cle: str, date: datetime.date):
        """
        Recherche les conversations contenant un message spécifique par mot-clé
        et correspondant à une date précise.

        Parameters
        ----------
        id_user : int
            Identifiant de l'utilisateur.
        mot_cle : str
            Mot-clé recherché dans les messages.
        date : datetime.date
            Date exacte (jour) des messages recherchés.

        Returns
        -------
        list[Conversation]
            Conversations répondant aux deux critères.

        Raises
        ------
        Exception
            Si la date n'est pas un objet datetime.date.
        """
        if not isinstance(date, datetime.date):
            raise Exception(f"la date {date} n'est pas au format date")
        if not isinstance(mot_cle, str) or not mot_cle.strip():
            return []
        pattern = f"%{mot_cle.strip()}%"
        with DBConnection().connection as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT DISTINCT c.id, c.titre, c.prompt_id, c.cree_le
                    FROM conversations c
                    JOIN conversations_participants cp
                    ON cp.conversation_id = c.id
                    JOIN messages m
                    ON m.conversation_id = c.id
                    WHERE cp.utilisateur_id = %(uid)s
                    AND DATE(m.cree_le) = %(d)s
                    AND m.contenu ILIKE %(pattern)s
                    ORDER BY c.cree_le DESC;
                    """,
                    {"uid": id_user, "d": date, "pattern": pattern},
                )
                rows = cur.fetchall() or []
        return [
            Conversation(
                id=r["id"],
                nom=r["titre"],
                personnalisation=r["prompt_id"],
                date_creation=r["cree_le"],
            )
            for r in rows
        ]

    @staticmethod
    def lire_echanges(id_conv: int, offset: int = 0, limit: int | None = 20) -> List[Echange]:
        """
        Récupère les échanges d'une conversation, avec ou sans pagination.

        Parameters
        ----------
        id_conv : int
            Identifiant de la conversation.
        offset : int, optional
            Nombre de messages à ignorer depuis les plus récents (mode pagination).
        limit : int | None, optional
            Nombre maximum de messages à retourner, ou None pour tout récupérer.

        Returns
        -------
        List[Echange]
            Liste d'objets Echange triés chronologiquement.

        Raises
        ------
        None
        """
        # Normalisation de offset
        if offset is None or offset < 0:
            offset = 0

        if limit is None:
            # TOUS les messages, du plus ancien au plus récent
            sql = """
                SELECT id, emetteur, contenu, cree_le
                FROM messages
                WHERE conversation_id = %(id_conv)s
                ORDER BY cree_le ASC, id ASC;
            """
            params = {"id_conv": id_conv}
        else:
            # Pagination sur LES DERNIERS messages
            if limit <= 0:
                limit = 20

            sql = """
                SELECT id, emetteur, contenu, cree_le
                FROM messages
                WHERE conversation_id = %(id_conv)s
                ORDER BY cree_le DESC, id DESC
                LIMIT %(limit)s OFFSET %(offset)s;
            """
            params = {"id_conv": id_conv, "limit": limit, "offset": offset}

        with DBConnection().connection as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall() or []

        echanges: List[Echange] = []
        for r in rows:
            e = Echange(
                id=r["id"],
                agent=r["emetteur"],
                message=r["contenu"],
                date_msg=r["cree_le"],
            )

            try:
                setattr(e, "agent", r["emetteur"])
                setattr(e, "date_msg", r["cree_le"])
            except Exception:
                pass

            echanges.append(e)

        # Si on est en mode pagination sur les "derniers",
        # on remet dans l'ordre chronologique (vieux -> récent)
        if limit is not None:
            echanges.reverse()

        return echanges

    def rechercher_echange(
        conversation_id: int, mot_clef: str, date: datetime.date
    ) -> list[Echange]:
        """
        Recherche des échanges dans une conversation, filtrés par mot-clé et date.

        Parameters
        ----------
        conversation_id : int
            Identifiant de la conversation.
        mot_clef : str
            Mot-clé recherché dans le contenu du message.
        date : datetime.date
            Date exacte des messages.

        Returns
        -------
        list[Echange]
            Liste des échanges trouvés.

        Raises
        ------
        Exception
            Si aucun échange ne correspond aux critères.
        """
        with DBConnection().connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT *
                    FROM messages
                    WHERE conversation_id = %(conversation_id)s
                    AND contenu ILIKE %(mot_clef)s
                    AND DATE(cree_le) = DATE(%(date)s);
                    """,
                    {"conversation_id": conversation_id, "mot_clef": f"%{mot_clef}%", "date": date},
                )
                res = cursor.fetchall()

            if not res:
                raise Exception(
                    f"Aucun échange trouvé pour la conversation {conversation_id} avec le mot-clé '{mot_clef}' à la date {date}"
                )

            liste_echanges = []
            for msg in res:
                liste_echanges.append(
                    Echange(
                        id=msg["id"],
                        agent=msg["emetteur"],
                        message=msg["contenu"],
                        date_msg=msg["cree_le"],
                    )
                )

            return liste_echanges

    def ajouter_participant(conversation_id: int, id_user: int, role: str) -> bool:
        """
        Ajoute un participant à une conversation.

        Parameters
        ----------
        conversation_id : int
            Identifiant de la conversation.
        id_user : int
            Identifiant de l’utilisateur à ajouter.
        role : str
            Rôle du participant (actuellement non utilisé).

        Returns
        -------
        bool
            True si l’ajout a réussi.

        Raises
        ------
        Exception
            Si l'utilisateur est déjà présent ou si l'insertion échoue.
        """
        with DBConnection().connection as conn:
            with conn.cursor() as cursor:
                #
                cursor.execute(
                    """
                    SELECT COUNT(*) as count
                    FROM conversations_participants
                    WHERE conversation_id = %(id_conv)s
                    AND utilisateur_id = %(id_user)s;
                    """,
                    {"id_conv": conversation_id, "id_user": id_user},
                )
                existe = cursor.fetchone()["count"]

                if existe > 0:
                    raise Exception(
                        f"L'utilisateur {id_user} est déjà participant de la conversation {conversation_id}"
                    )

                cursor.execute(
                    """
                    INSERT INTO conversations_participants (conversation_id, utilisateur_id)
                    VALUES (%(conversation_id)s, %(id_user)s);
                    """,
                    {"conversation_id": conversation_id, "id_user": id_user},
                )
                count = cursor.rowcount

            if count > 0:
                return True
            else:
                raise Exception(
                    f"Erreur lors de l'ajout de l'utilisateur {id_user} à la conversation {conversation_id}"
                )

    def retirer_participant(conversation_id: int, id_user: int) -> bool:
        """
        Retire un participant d’une conversation.

        Parameters
        ----------
        conversation_id : int
            Identifiant de la conversation.
        id_user : int
            Identifiant de l’utilisateur à retirer.

        Returns
        -------
        bool
            True si le retrait a réussi.

        Raises
        ------
        Exception
            Si la conversation n’a qu’un seul participant
            ou si l’utilisateur n’est pas présent.
        """
        with DBConnection().connection as conn:
            with conn.cursor() as cursor:
                #
                cursor.execute(
                    """
                    SELECT COUNT(*) as count
                    FROM conversations_participants
                    WHERE conversation_id = %(id_conv)s;
                    """,
                    {"id_conv": conversation_id},
                )
                nb_participants = cursor.fetchone()["count"]

                if nb_participants <= 1:
                    raise Exception(
                        f"Impossible de retirer le dernier participant de la conversation {conversation_id}"
                    )

                cursor.execute(
                    """
                    DELETE FROM conversations_participants
                    WHERE conversation_id = %(id_conv)s
                    AND utilisateur_id = %(id_user)s;
                    """,
                    {"id_conv": conversation_id, "id_user": id_user},
                )
                count = cursor.rowcount

        if count > 0:
            return True
        else:
            raise Exception(
                f"L'utilisateur {id_user} n'est pas participant de la conversation {conversation_id}"
            )

    @staticmethod
    def ajouter_echange(id_conv: int, echange: Echange) -> bool:
        """
        Ajoute un message dans une conversation.

        Parameters
        ----------
        id_conv : int
            Identifiant de la conversation.
        echange : Echange
            Objet contenant un message, son émetteur et éventuellement l'utilisateur associé.

        Returns
        -------
        bool
            True si l’ajout s’est bien passé.

        Raises
        ------
        Exception
            Si l'émetteur est invalide ou si un utilisateur_id est manquant.
        """
        emetteur = getattr(echange, "emetteur", None) or getattr(echange, "expediteur", None)
        contenu = getattr(echange, "contenu", None) or getattr(echange, "message", None)
        utilisateur_id = getattr(echange, "utilisateur_id", None)

        if emetteur not in ("utilisateur", "ia"):
            raise Exception(f"emetteur invalide: {emetteur!r} (attendu 'utilisateur' ou 'ia')")

        # Contrainte fonctionnelle cohérente avec le CHECK de la table
        if emetteur == "utilisateur" and utilisateur_id is None:
            raise Exception("utilisateur_id requis quand emetteur='utilisateur'")

        with DBConnection().connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO messages (conversation_id, utilisateur_id, emetteur, contenu)
                    VALUES (%(conversation_id)s, %(utilisateur_id)s, %(emetteur)s, %(contenu)s)
                    RETURNING id;
                    """,
                    {
                        "conversation_id": id_conv,
                        "utilisateur_id": utilisateur_id,
                        "emetteur": emetteur,
                        "contenu": contenu,
                    },
                )
                echange.id = cursor.fetchone()["id"]
        return True

    @staticmethod
    def mettre_a_j_preprompt_id(conversation_id: int, prompt_id: int) -> bool:
        """
        Met à jour la personnalisation (prompt) d'une conversation.

        Parameters
        ----------
        conversation_id : int
            Identifiant de la conversation.
        prompt_id : int
            Identifiant du nouveau préprompt (profil IA).

        Returns
        -------
        str
            Message de confirmation.

        Raises
        ------
        Exception
            Si la mise à jour n'a pas modifié de ligne.
        """
        with DBConnection().connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE conversations
                    SET prompt_id = %(prompt_id)s
                    WHERE id = %(conversation_id)s
                    """,
                    {"prompt_id": prompt_id, "conversation_id": conversation_id},
                )
                count = cursor.rowcount
        if count > 0:
            return "personnalité modifié avec succès"
        else:
            raise Exception(
                f"Erreur dans la modification de la personnalisation pour conversation_id = {conversation_id}"
            )

    @staticmethod
    def compter_conversations(id_user: int) -> int:
        """
        Compte toutes les conversations auxquelles un utilisateur participe.

        Parameters
        ----------
        id_user : int
            Identifiant de l'utilisateur.

        Returns
        -------
        int
            Nombre total de conversations.
        """
        liste_CONV = ConversationDAO.lister_conversations(id_user=id_user)
        return len(liste_CONV)

    @staticmethod
    def compter_message_user(id_user: int) -> int:
        """
        Compte le nombre total de messages envoyés par un utilisateur.

        Parameters
        ----------
        id_user : int
            Identifiant de l'utilisateur.

        Returns
        -------
        int
            Nombre total de messages envoyés par l'utilisateur.

        Raises
        ------
        None
        """
        with DBConnection().connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                SELECT COUNT(*)
                FROM message m
                WHERE m.utilisateur_id = %(id_user)d AND m.emetteur = 'utilisateur'
                """,
                    {"id_user": id_user},
                )
                nombre_messages = cursor.fetchall()
        return nombre_messages

    @staticmethod
    def sujets_plus_frequents(id_user: int, k: int) -> list[tuple[str, int]]:
        """
        Détermine les sujets les plus fréquents dans les titres des conversations d’un utilisateur.

        Parameters
        ----------
        id_user : int
            Identifiant de l'utilisateur.
        k : int
            Nombre de sujets les plus fréquents à retourner.

        Returns
        -------
        list[tuple[str, int]]
            Liste des paires (mot, fréquence).

        Raises
        ------
        Exception
            Si l'utilisateur n'a aucune conversation.
        """
        query = """
            SELECT c.titre
            FROM conversations c
            JOIN conversations_participants uc ON c.id = uc.conversation_id
            WHERE uc.utilisateur_id = %(id_user)s;
            """

        with DBConnection().connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, {"id_user": id_user})
                titres = [row["titre"] for row in cursor.fetchall()]

        if not titres:
            raise Exception(f"Aucune conversation trouvée pour l'utilisateur {id_user}")

        # Liste de mots à ignorer (articles, prépositions courantes, etc.)
        stop_words = {
            "le",
            "la",
            "les",
            "de",
            "des",
            "du",
            "un",
            "une",
            "et",
            "en",
            "à",
            "a",
            "au",
            "aux",
            "pour",
            "par",
            "avec",
            "sur",
            "dans",
            "d",
            "l",
            "l'",
            "au",
            "aux",
        }

        mots = []
        for titre in titres:
            # Mettre en minuscules et retirer la ponctuation
            titre_nettoye = re.sub(r"[^\w\s']", " ", titre.lower())
            # Séparer en mots
            for mot in titre_nettoye.split():
                # Nettoyer les apostrophes
                mot = re.sub(r"^l['’]", "", mot)
                # Ajouter seulement si ce n'est pas un mot vide
                if mot and mot not in stop_words:
                    mots.append(mot)

        compteur = Counter(mots)
        sujets_frequents = compteur.most_common(k)

        return sujets_frequents
