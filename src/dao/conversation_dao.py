import re
from collections import Counter
from datetime import datetime
from datetime import datetime as Date

from business_object.conversation import Conversation
from business_object.echange import Echange
from dao.db_connection import DBConnection
from dao.prompt_dao import PromptDAO


class ConversationDAO:
    @staticmethod
    def creer_conversation(conversation: Conversation) -> Conversation:
        """
        Insère dans `conversations` uniquement (titre, prompt_id). Pas d'owner ici.
        - conversation.nom  -> titre
        - conversation.personnalisation (nom de prompt | id | None) -> prompt_id
        """
        # Titre obligatoire
        titre = (conversation.nom or "").strip()
        if not titre:
            raise ValueError("Le nom (titre) de la conversation est obligatoire.")

        # Résoudre prompt_id :
        perso = conversation.personnalisation
        prompt_id = None
        if isinstance(perso, str):
            perso = perso.strip()
            if perso:  # nom de prompt fourni
                prompt_id = PromptDAO.get_id_by_name(perso)
                if prompt_id is None:
                    raise ValueError(f"Prompt inconnu : '{perso}'")
        elif isinstance(perso, int):
            # ID fourni directement
            if not PromptDAO.exists_id(perso):
                raise ValueError(f"prompt_id inexistant: {perso}")
            prompt_id = perso
        else:
            # None ou vide -> pas de prompt
            prompt_id = None

        with DBConnection().connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO conversations (titre, prompt_id)
                    VALUES (%(titre)s, %(prompt_id)s)
                    RETURNING id, cree_le;
                    """,
                    {"titre": titre, "prompt_id": prompt_id},  # None -> NULL (OK)
                )
                row = cursor.fetchone()
                conversation.id = row["id"]
                conversation.date_creation = row["cree_le"]
                # On peut conserver dans l'objet l'id résolu (ou None)
                conversation.personnalisation = prompt_id

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
    def renommer_conv(id_conv: int, nouveau_nom: str) -> bool:
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
    def supprimmer_conv(id_conv: int) -> str:
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
            return f"la conversation d'id={id_conv} a bien été supprimmée"
        else:
            raise Exception(f"echec de la suppression de la conversation d'identifiant {id_conv}")

    @staticmethod
    def lister_conversations(id_user: int, n=None) -> list[Conversation]:
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
    def rechercher_mot_clef(self, id_user: int, mot_clef: str) -> list[Conversation]:
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
        liste_CONV = ConversationDAO.lister_conversation(id_user)
        liste_conv = [conv.id for conv in liste_CONV]
        # on récupère d'abord tous les identifiants des conversations qui vérifient comprennent au moins un
        # message avec le mot_clef, pour un utilisateur donné.
        with DBConnection().connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT conversation_id
                    FROM messages 
                    WHERE conversation_id = ANY(%(conv_id)s)
                    AND contenu ILIKE%(mot_clef)s;
                    """,
                    {"conv_id": liste_conv, "mot_clef": mot_clef},
                )
                liste = cursor.fetchall()
            liste = set(liste)
            if not liste:
                raise Exception(
                    f"aucune conversation trouvée parmi les conversations de l'utilisateur {id_user} our le mot clé '{mot_clef}'"
                )
            # une fois qu'on a récupéré la liste des conversations_id, on récupère les conversations
            # depuis la table conversations (oui je sais on aurait pu fair un join mais flemme)
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT*
                    FROM conversations
                    WHERE id = ANY(%(conv_id))
                    """,
                    {"conv_id": liste},
                )
                res = cursor.fetchall()
            liste_finale = []
            for conv in res:
                liste_finale.append(
                    Conversation(
                        id=conv["id"],
                        nom=conv["titre"],
                        personnalisation=conv["prompt_id"],
                        date_creation=conv["cree_le"],
                    )
                )
            return liste_finale

    @staticmethod
    def rechercher_date(id_user: int, date: Date) -> list[Conversation]:
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
        # contrôle du format de la date:
        if not isinstance(date, datetime):
            raise Exception(f"la date {date} n'est pas au format datetime")

        # on récupère tous les identifiants de conversation qui ont des messages qui correspondent

        # à la date en entrée.
        with DBConnection().connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT conversation_id
                    FROM messages
                    WHERE cree_le = %(date)s
                    AND utilisateur_id = %(id_user)s;
                    """,
                    {"date": date, "id_user": id_user},
                )
                dict_id = cursor.fetchall()
            if not dict_id:
                raise Exception(
                    f"Aucune conversation de l'utilisateur {id_user} pour la date {date}"
                )
            # on récupère
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT *
                    FROM conversations
                    WHERE id = ANY(%(dict_id)s);
                    """,
                    {"dict_id": dict_id},
                )
                res = cursor.fetchall()
            liste_res = []
            for conv in res:
                liste_res.append(
                    Conversation(
                        id=conv["id"],
                        nom=conv["titre"],
                        personnalisation=conv["prompt_id"],
                        date_creation=conv["cree_le"],
                    )
                )

            return liste_res

    def rechercher_conv_motC_et_date(id_user: int, mot_cle: str, date: datetime.date):
        # contrôle du format de la date:
        if not isinstance(date, datetime.date):
            raise Exception(f"la date {date} n'est pas au format datetime")
        if not isinstance(mot_cle, str):
            raise Exception("le mot clé n'est pas une chaîne de charactères")
        # on récupère tous les identifiants de conversation qui ont des messages qui correspondent
        # à la date en entrée et qui comprennent le mot_clé.
        with DBConnection().connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT conversation_id
                    FROM messages
                    WHERE DATE(cree_le) = %(date)s
                    AND utilisateur_id = %(id_user)s
                    AND contenu ILIKE %(mot_cle)s;
                    """,
                    {"date": date, "id_user": id_user, "mot_cle": f"%{mot_cle}%"},
                )
                dict_id = cursor.fetchall()
            if not dict_id:
                raise Exception(
                    f"Aucune conversation de l'utilisateur {id_user} pour la date {date}"
                )
            ids = [row["conversation_id"] for row in dict_id]

            # on récupère les conversations de ids
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT *
                    FROM conversations
                    WHERE id = ANY(%(ids)s);
                    """,
                    {"dict_id": tuple(ids)},
                )
                res = cursor.fetchall()
            liste_res = []
            for conv in res:
                liste_res.append(
                    Conversation(
                        id=conv["id"],
                        nom=conv["titre"],
                        personnalisation=conv["prompt_id"],
                        date_creation=conv["cree_le"],
                    )
                )

            return liste_res

    @staticmethod
    def lire_echanges(id_conv: int, limit: int) -> list[Echange]:
        """
        Permet de lire les messages d'une conversation donnée.

        Parameters
        ----------
            id_conv : int
                l'identifiant du joueur

        Returns
        -------
            List[Echange]


        Raises
        ------
        """
        with DBConnection().connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT * 
                    FROM messages 
                    WHERE conversation_id = %(id_conv)s
                    """,
                    {"id_conv": id_conv},
                )
                res = cursor.fetchall()
            if not res:
                raise Exception(f"pas de messages trouvés pour l'identifiant {id_conv}")
            else:
                liste_conv = []
                for conv in res:
                    liste_conv.append(
                        Echange(
                            id=conv["id"],
                            agent=conv["emetteur"],
                            message=conv["contenu"],
                            date_msg=conv["cree_le"],
                        )
                    )
                return liste_conv

    def rechercher_echange(conversation_id: int, mot_clef: str, date: Date) -> list[Echange]:
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
                    {"id_conv": conversation_id, "mot_clef": f"%{mot_clef}%", "date": date},
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
        with DBConnection().connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO messages (conversation_id, utilisateur_id, emetteur, contenu)
                        VALUES (%(conversation_id)d, %(utilisateur_id)d, %(emetteur)s, %(contenu)s)                          
                    RETURNING id;
                    """,
                    {
                        "conversation_id": id_conv,
                        "utilisateur_id": echange.utilisateur_id,
                        "emetteur": echange.emetteur,
                        "contenu": echange.contenu,
                    },
                )
                echange.id = cursor.fetchone()["id"]
        return echange

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
    def sujets_plus_frequents(id_user: int, k: int) -> list[str]:
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
