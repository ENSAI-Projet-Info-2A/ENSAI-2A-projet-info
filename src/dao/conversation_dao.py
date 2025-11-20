import datetime
import logging
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
        logging.debug(
            "Création conversation : nom=%r, proprietaire_id=%r, personnalisation=%r",
            getattr(conversation, "nom", None),
            proprietaire_id,
            getattr(conversation, "personnalisation", None),
        )

        # Vérification / nettoyage du titre
        titre = (conversation.nom or "").strip()
        if not titre:
            raise ValueError("Le nom (titre) de la conversation est obligatoire.")

        # Résolution du prompt_id à partir de `conversation.personnalisation`
        perso = conversation.personnalisation
        prompt_id: int | None = None

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
        else:
            # perso est None ou un type non géré -> pas de prompt
            prompt_id = None

        # Insertion en base
        with DBConnection().connection as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO conversations (titre, prompt_id, proprietaire_id)
                    VALUES (%(titre)s, %(prompt_id)s, %(proprietaire_id)s)
                    RETURNING id, cree_le, proprietaire_id;
                    """,
                    {
                        "titre": titre,
                        "prompt_id": prompt_id,
                        "proprietaire_id": proprietaire_id,
                    },
                )
                row = cur.fetchone()
                conversation.id = row["id"]
                conversation.date_creation = row["cree_le"]
                conversation.personnalisation = prompt_id
                # Nécessite que Conversation ait un attribut `proprietaire_id`
                conversation.proprietaire_id = row["proprietaire_id"]

                # (optionnel) On ajoute aussi le propriétaire comme participant
                if proprietaire_id is not None:
                    cur.execute(
                        """
                        INSERT INTO conversations_participants (conversation_id, utilisateur_id)
                        VALUES (%(cid)s, %(uid)s)
                        ON CONFLICT DO NOTHING;
                        """,
                        {"cid": conversation.id, "uid": proprietaire_id},
                    )

        logging.info(
            "Conversation créée (id=%s, titre=%r, prompt_id=%r, proprietaire_id=%r)",
            conversation.id,
            conversation.nom,
            conversation.personnalisation,
            getattr(conversation, "proprietaire_id", None),
        )
        return conversation

    @staticmethod
    def est_proprietaire(conversation_id: int, utilisateur_id: int) -> bool:
        logging.debug(
            "Vérification propriétaire : conv_id=%s, user_id=%s",
            conversation_id,
            utilisateur_id,
        )
        with DBConnection().connection as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 1
                    FROM conversations
                    WHERE id = %(cid)s
                      AND proprietaire_id = %(uid)s;
                    """,
                    {"cid": conversation_id, "uid": utilisateur_id},
                )
                res = cur.fetchone() is not None
        logging.debug(
            "Résultat vérification propriétaire (conv_id=%s, user_id=%s) -> %s",
            conversation_id,
            utilisateur_id,
            res,
        )
        return res

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
        logging.debug("Recherche conversation par id=%s", id_conv)
        with DBConnection().connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, titre, prompt_id, cree_le, proprietaire_id
                    FROM conversations
                    WHERE id = %(id_conv)s;
                    """,
                    {"id_conv": id_conv},
                )
                conv = cursor.fetchone()
        if not conv:
            logging.warning("Aucune conversation trouvée avec id=%s", id_conv)
            raise Exception(f"Aucune conversation trouvée avec id={id_conv}")
        logging.info(
            "Conversation trouvée (id=%s, titre=%r, prompt_id=%r)",
            conv["id"],
            conv["titre"],
            conv["prompt_id"],
        )
        return Conversation(
            id=conv["id"],
            nom=conv["titre"],
            personnalisation=conv["prompt_id"],
            date_creation=conv["cree_le"],
            proprietaire_id=conv["proprietaire_id"],
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
        logging.debug(
            "Renommage conversation demandé (id=%s -> nouveau_nom=%r)",
            id_conv,
            nouveau_nom,
        )
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
            logging.info("Titre conversation modifié avec succès (id=%s)", id_conv)
            return "titre modifié avec succès"
        else:
            logging.warning("Aucune conversation renommée (id_conv=%s, rowcount=0)", id_conv)
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
        logging.debug("Suppression conversation demandée (id=%s)", id_conv)
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
            logging.info("Conversation supprimée (id=%s)", id_conv)
            return f"la conversation d'id={id_conv} a bien été supprimée"
        else:
            logging.warning("Échec suppression conversation (id=%s, rowcount=0)", id_conv)
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
        logging.debug(
            "Listing conversations pour user_id=%s avec limite=%r",
            id_user,
            n,
        )
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
        logging.info(
            "Conversations listées pour user_id=%s (nb=%s)",
            id_user,
            len(rows),
        )
        return [
            Conversation(
                id=row["id"],
                nom=row["titre"],
                personnalisation=row["prompt_id"],
                date_creation=row["cree_le"],
                proprietaire_id=row["proprietaire_id"],
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
        logging.debug(
            "Recherche conversations par mot-clé pour user_id=%s, mot_clef=%r",
            id_user,
            mot_clef,
        )
        if not isinstance(mot_clef, str) or not mot_clef.strip():
            return []
        pattern = f"%{mot_clef.strip()}%"
        with DBConnection().connection as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT DISTINCT c.id, c.titre, c.prompt_id, c.proprietaire_id, c.cree_le
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
        logging.info(
            "Recherche mot-clé pour user_id=%s, mot_clef=%r -> %s conversation(s)",
            id_user,
            mot_clef,
            len(rows),
        )
        return [
            Conversation(
                id=r["id"],
                nom=r["titre"],
                personnalisation=r["prompt_id"],
                date_creation=r["cree_le"],
                proprietaire_id=r["proprietaire_id"],
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
        logging.debug(
            "Recherche conversations par date pour user_id=%s, date=%r",
            id_user,
            date,
        )
        # Normalisation du paramètre "date" en début/fin de journée
        if isinstance(date, datetime.date) and not isinstance(date, datetime.datetime):
            d0 = datetime.datetime(date.year, date.month, date.day)
        elif isinstance(date, datetime.datetime):
            d0 = datetime.datetime(date.year, date.month, date.day)
        else:
            raise Exception(f"la date {date!r} n'est pas au format datetime/date")

        d1 = d0 + datetime.timedelta(days=1)

        sql = """
            SELECT DISTINCT c.id, c.titre, c.prompt_id, c.proprietaire_id, c.cree_le
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

        logging.info(
            "Recherche par date pour user_id=%s, date=%s -> %s conversation(s)",
            id_user,
            d0.date(),
            len(rows),
        )
        return [
            Conversation(
                id=r["id"],
                nom=r["titre"],
                personnalisation=r["prompt_id"],
                date_creation=r["cree_le"],
                proprietaire_id=r["proprietaire_id"],
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
        logging.debug(
            "Recherche conversations mot+date (user_id=%s, mot_cle=%r, date=%r)",
            id_user,
            mot_cle,
            date,
        )
        if not isinstance(date, datetime.date):
            raise Exception(f"la date {date} n'est pas au format date")
        if not isinstance(mot_cle, str) or not mot_cle.strip():
            return []
        pattern = f"%{mot_cle.strip()}%"
        with DBConnection().connection as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT DISTINCT c.id, c.titre, c.prompt_id, c.proprietaire_id, c.cree_le
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
        logging.info(
            "Recherche mot+date pour user_id=%s, mot_cle=%r, date=%s -> %s conversation(s)",
            id_user,
            mot_cle,
            date,
            len(rows),
        )
        return [
            Conversation(
                id=r["id"],
                nom=r["titre"],
                personnalisation=r["prompt_id"],
                date_creation=r["cree_le"],
                proprietaire_id=r["proprietaire_id"],
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
        logging.debug(
            "Lecture échanges pour conv_id=%s (offset=%s, limit=%r)",
            id_conv,
            offset,
            limit,
        )
        # Normalisation de offset
        if offset is None or offset < 0:
            offset = 0

        # --- Construction de la requête SQL avec JOIN sur utilisateurs ---
        if limit is None:
            # Tous les messages
            sql = """
                SELECT
                    m.id,
                    m.emetteur,
                    m.contenu,
                    m.cree_le,
                    m.utilisateur_id,
                    u.pseudo AS utilisateur_pseudo
                FROM messages m
                LEFT JOIN utilisateurs u ON u.id = m.utilisateur_id
                WHERE m.conversation_id = %(id_conv)s
                ORDER BY m.cree_le ASC, m.id ASC;
            """
            params = {"id_conv": id_conv}
        else:
            if limit <= 0:
                limit = 20

            sql = """
                SELECT
                    m.id,
                    m.emetteur,
                    m.contenu,
                    m.cree_le,
                    m.utilisateur_id,
                    u.pseudo AS utilisateur_pseudo
                FROM messages m
                LEFT JOIN utilisateurs u ON u.id = m.utilisateur_id
                WHERE m.conversation_id = %(id_conv)s
                ORDER BY m.cree_le DESC, m.id DESC
                LIMIT %(limit)s OFFSET %(offset)s;
            """
            params = {"id_conv": id_conv, "limit": limit, "offset": offset}

        # --- Exécution SQL ---
        with DBConnection().connection as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall() or []

        # --- Construction des objets Echange ---
        echanges: List[Echange] = []
        for r in rows:
            emetteur = r["emetteur"]  # 'utilisateur' ou 'ia'
            pseudo = r.get("utilisateur_pseudo")  # nom utilisateur ou None
            # Nom pour affichage
            if emetteur == "ia":
                agent_name = "Assistant"
            else:
                agent_name = pseudo or "Utilisateur"

            # Création de l'objet Echange enrichi
            e = Echange(
                id=r["id"],
                agent=emetteur,  # conserve la valeur brute pour le LLM
                message=r["contenu"],
                date_msg=r["cree_le"],
                agent_name=agent_name,  # <-- nom affiché
            )

            # Champs supplémentaires pour compatibilité
            setattr(e, "emetteur", emetteur)
            setattr(e, "utilisateur_id", r["utilisateur_id"])

            echanges.append(e)

        # Si on a utilisé LIMIT/OFFSET → remettre dans l'ordre chronologique
        if limit is not None:
            echanges.reverse()

        logging.info(
            "Lecture échanges terminée pour conv_id=%s (nb_messages=%s)",
            id_conv,
            len(echanges),
        )
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
        logging.debug(
            "Recherche échanges pour conv_id=%s, mot_clef=%r, date=%r",
            conversation_id,
            mot_clef,
            date,
        )
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
                logging.warning(
                    "Aucun échange trouvé (conv_id=%s, mot_clef=%r, date=%s)",
                    conversation_id,
                    mot_clef,
                    date,
                )
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

            logging.info(
                "Recherche échanges terminée (conv_id=%s, nb=%s)",
                conversation_id,
                len(liste_echanges),
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
        logging.debug(
            "Ajout participant demandé (conv_id=%s, user_id=%s, role=%r)",
            conversation_id,
            id_user,
            role,
        )
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
                    logging.warning(
                        "Ajout participant impossible : user_id=%s déjà dans conv_id=%s",
                        id_user,
                        conversation_id,
                    )
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
                logging.info(
                    "Participant ajouté (conv_id=%s, user_id=%s)",
                    conversation_id,
                    id_user,
                )
                return True
            else:
                logging.warning(
                    "Ajout participant échoué (conv_id=%s, user_id=%s, rowcount=0)",
                    conversation_id,
                    id_user,
                )
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
        logging.debug(
            "Retrait participant demandé (conv_id=%s, user_id=%s)",
            conversation_id,
            id_user,
        )
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
                    logging.warning(
                        "Impossible de retirer le dernier participant (conv_id=%s)",
                        conversation_id,
                    )
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
            logging.info(
                "Participant retiré (conv_id=%s, user_id=%s)",
                conversation_id,
                id_user,
            )
            return True
        else:
            logging.warning(
                "Retrait participant échoué : user_id=%s non trouvé dans conv_id=%s",
                id_user,
                conversation_id,
            )
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
        emetteur = (
            getattr(echange, "emetteur", None)
            or getattr(echange, "expediteur", None)
            or getattr(echange, "agent", None)  # <- on ajoute ça pour prendre en compte une modif
        )
        contenu = getattr(echange, "contenu", None) or getattr(echange, "message", None)
        utilisateur_id = getattr(echange, "utilisateur_id", None)

        logging.debug(
            "Ajout échange (conv_id=%s, emetteur=%r, utilisateur_id=%r)",
            id_conv,
            emetteur,
            utilisateur_id,
        )

        if emetteur not in ("utilisateur", "ia"):
            logging.error("emetteur invalide pour ajout échange : %r", emetteur)
            raise Exception(f"emetteur invalide: {emetteur!r} (attendu 'utilisateur' ou 'ia')")

        # Contrainte fonctionnelle cohérente avec le CHECK de la table
        if emetteur == "utilisateur" and utilisateur_id is None:
            logging.error("utilisateur_id manquant pour ajout échange (emetteur='utilisateur')")
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
        logging.info(
            "Échange ajouté (conv_id=%s, message_id=%s, emetteur=%r)",
            id_conv,
            getattr(echange, "id", None),
            emetteur,
        )
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
        logging.debug(
            "Mise à jour prompt_id (conv_id=%s -> prompt_id=%s)",
            conversation_id,
            prompt_id,
        )
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
            logging.info(
                "Personnalisation mise à jour (conv_id=%s, prompt_id=%s)",
                conversation_id,
                prompt_id,
            )
            return "personnalité modifié avec succès"
        else:
            logging.warning(
                "Aucune ligne modifiée pour mise à jour prompt (conv_id=%s)",
                conversation_id,
            )
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
        logging.debug("Comptage conversations pour user_id=%s", id_user)
        liste_CONV = ConversationDAO.lister_conversations(id_user=id_user)
        total = len(liste_CONV)
        logging.info(
            "Nombre total de conversations pour user_id=%s : %s",
            id_user,
            total,
        )
        return total

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
        """
        logging.debug("Comptage messages utilisateur pour user_id=%s", id_user)
        with DBConnection().connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*) AS nb
                    FROM messages m
                    WHERE m.utilisateur_id = %(id_user)s
                      AND m.emetteur = 'utilisateur';
                    """,
                    {"id_user": id_user},
                )
                row = cursor.fetchone()  # row est un dict avec RealDictCursor, ex: {"nb": 12}

        if not row or row["nb"] is None:
            logging.info(
                "Aucun message trouvé pour user_id=%s (count=0)",
                id_user,
            )
            return 0

        total = int(row["nb"])
        logging.info(
            "Nombre de messages utilisateur pour user_id=%s : %s",
            id_user,
            total,
        )
        return total

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
        logging.debug(
            "Calcul sujets plus fréquents pour user_id=%s (top k=%s)",
            id_user,
            k,
        )
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
            logging.warning(
                "Aucune conversation trouvée pour sujets fréquents (user_id=%s)",
                id_user,
            )
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

        logging.info(
            "Sujets les plus fréquents pour user_id=%s : %r",
            id_user,
            sujets_frequents,
        )
        return sujets_frequents
