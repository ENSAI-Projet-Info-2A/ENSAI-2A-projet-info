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
        Renomme une conversation dans la base de donnée:

        Parameters
        ----------
            id_conv : int
                identifiant de la conversation
            nouveau_nom : str
                le nouveau nom souhaité

        Returns
        -------
            bool
                indique si le nom a été changé avec succès

        Raises
        ------
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
        Supprimme une conversation dans la base de donnée.

        Parameters
        ----------
            id_conv : int
                identifiant de la conversation

        Returns
        -------
            str
                Indique si la conversation a été supprimée avec succès.

        Raises
        ------
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
        query = """
            SELECT *
            FROM projet_test_dao.conversations
            WHERE id IN (
                SELECT m.conversation_id
                FROM projet_test_dao.messages AS m
                JOIN projet_test_dao.conversations_participants AS cp
                ON m.conversation_id = cp.conversation_id
                WHERE cp.utilisateur_id = %(id_user)s
                GROUP BY m.conversation_id
            )
            ORDER BY (
                SELECT MAX(m2.cree_le)
                FROM projet_test_dao.messages AS m2
                WHERE m2.conversation_id = conversations.id
            ) DESC;
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
        Recherche une conversation selon un mot-clé.

        Parameters
        ----------
            id_user : int
                l'identifiant d'un utilisateur
            mot_clef : str
                le mot-clé avec lequel on fait la recherche.

        Returns
        -------
            List[Conversation]
                Une liste d'objet Conversation qui incluent le mot-clé.

        Raises
        ------
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
                    JOIN messages m
                    ON m.conversation_id = c.id
                    WHERE cp.utilisateur_id = %(uid)s
                    AND m.contenu ILIKE %(pattern)s
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

        Recherche une conversation à partir d'une date (date d'un message)


        Parameters
        ----------
            id_user : int
                l'identifiant d'un utilisateur
            date : Date
                un objet Date

        Returns
        -------
            List[Conversation]
                Une liste de Conversations qui correspondent à la date.

        Raises
        ------
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

    def rechercher_conv_motC_et_date(id_user: int, mot_cle: str, date: datetime.date):
        """
        Retourne les conversations avec au moins un message contenant `mot_cle`
        ET daté le jour `date` (peu importe l'heure), émis par l'utilisateur.
        ATTENTION: attend un `date` (pas un `datetime`).
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
    def lire_echanges(id_conv: int, offset: int = 0, limit: int = 20) -> List[Echange]:
        """
        Retourne les messages d'une conversation, triés du plus ancien au plus récent,
        avec pagination SQL (offset/limit).
        """
        if limit <= 0:
            limit = 20
        if offset < 0:
            offset = 0

        sql = """
            SELECT id, emetteur, contenu, cree_le
            FROM messages
            WHERE conversation_id = %(id_conv)s
            ORDER BY cree_le ASC, id ASC
            LIMIT %(limit)s OFFSET %(offset)s;
        """

        with DBConnection().connection as conn:
            with conn.cursor() as cur:
                cur.execute(sql, {"id_conv": id_conv, "limit": limit, "offset": offset})
                rows = cur.fetchall() or []

        echanges: List[Echange] = []
        for r in rows:
            e = Echange(
                id=r["id"],
                agent=r["emetteur"],
                message=r["contenu"],
                date_msg=r["cree_le"],
            )

            # Compatibilité éventuelle avec d'autres attributs
            try:
                setattr(e, "agent", r["emetteur"])
                setattr(e, "date_msg", r["cree_le"])
            except Exception:
                pass

            echanges.append(e)

        return echanges

    def rechercher_echange(
        conversation_id: int, mot_clef: str, date: datetime.date
    ) -> list[Echange]:
        """
        Recherche un échange au sein d'une conversation, à partir d'un mot-clé et d'une date.

        Parameters
        ----------
            id_conv : int
                l'identifiant d'une conversation
            mot_clef : str
                Le mot-clef de la recherche
            date : Date
                la date supposée de l'échange

        Returns
        -------
            list[Echange]
                Une liste d'objets Echanges qui répondent à la recherche

        Raises
        ------
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
        Ajoute un autre utilisateur à une conversation en cours.

        Parameters
        ----------
            id_conv : int
                identifiant de la conversation
            id_user : int
                identifiant du joueur à rajouter
            role : str
                ?

        Returns
        -------
            bool
                indique si le joueur a été ajouté ou non
        Raises
        ------
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
        Retire un utilisateur d'une conversation. (comment borner le droit :
        éviter qu'un mec invité tej le proprio de la conv?)

        Parameters
        ----------
            id_conv : int
                identifiant de la conversation dont on veut retirer un des participants.
            id_user : int
                identifiant du joueur à retirer de la conversation

        Returns
        -------
            Bool
                indique si le joueur a été effectivement retiré
        Raises
        ------
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
        Ajoute un échange à une conversation dans la base de donnée.

        Parameters
        ----------
            id_conv : int
                Description du paramètre 1.
            param2 : Type2
                Description du paramètre 2.

        Returns
        -------
            ReturnType
                Description de ce que la méthode retourne.

        Raises
        ------
            ExceptionType
                Description des exceptions levées (optionnel).
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
        Permet de changer le profil du LLM via un système de préprompt

        Parameters
        ----------
            id_conv : int
                l'identifiant de la conversation pour laquelle on veut changer le profil du LLM
                preprompt_id : str
                Nom du profil du LLM à appliquer

        Returns
        -------__
            Bool
                indique si le profil du LLM a été changé avec succès
        Raises
        ------
        """
        with DBConnection().connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE conversations
                    SET prompt_id = %(prompt_id)d
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
        Compte le nombre total de conversation d'un utilisateur (compter aussi conv auxquelles il est invité ?).

        Parameters
        ----------
            id_user : int
                l'identifiant de l'utilisateur dans la base de donnée

        Returns
        -------
            int
                Le nombre total de conversations de l'utilisateur.

        Raises
        ------
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
                l'identifiant de l'utilisateur dans la base de donnée

        Returns
        -------
            int
                Le nombre total de messages envoyé.

        Raises
        ------
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
    def sujets_plus_frequents(id_user: int, k: int) ->list[tuple[str, int]]:
        """
        Renvoie une liste des sujets les plus fréquents entretenus dans les conversations d'un utilisateur.

        Parameters
        ----------
            id_user : int
                l'identifiant de l'utilisateur dans la base de donnée
            k : int
                nombres k de sujets les plus fréquents considérés

        Returns
        -------
            List[str]
                Une liste des principaux sujets déterminés par le LLM

        Raises
        ------
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
