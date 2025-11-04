from datetime import datetime as Date

from business_object.conversation import Conversation

import psycopg2.extras
from business_object.echange import Echange
from dao.db_connection import DBConnection

class ConversationDAO: 
    
    ####faudra revenir dessus car il manque potentiellement le param preprompt_id/traduction
    #### faut rajouter aussi 
    def create(self, conversation):
        """
        créer une nouvelle conversation dans la table Conversation

        Parameters
        ----------
            conversation : int
                identifiant de la conversation
        """
        with DBConnection().connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO conversations (titre, prompt_id, cree_le)         
                        VALUES (%(titre)s, %(prompt_id)s, %(cree_le)s)           
                    RETURNING id;
                    """,
                    {"titre": conversation.titre, 
                    "prompt_id": prompt_id, 
                    "cree_le": cree_le}
                    )
                conversation.id = cursor.fetchone()["id"]
        return conversation

        pass



    def trouver_par_id(id_conv: int) -> Conversation:
        """
        Trouve une conversation dans la base de donnée à partir de son identifiant.

        Parameters
        ----------
            id_conv : int
                identifiant de la conversation


        Returns
        -------
            Conversation
                la conversation correspondant à l'identifiant en entrée

        Raises
        ------
        """
        with DBConnection().connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id_conv, titrpreprompt_id, , cree_le    
                    FROM conversations WHERE id = %(id_conv)s ;
                    """,
                    {"id_conv" : id_conv}
                )
                conv = cursor.fetchone()
            if conv:
                return Conversation(id= conv["id"], nom= conv["titre"], 
                    personnalisation = conv["prompt_id"], date_creation = conv["cree_le"])
            else:
                raise Exception(f"Aucune conversation trouvée avec id_conv={id_conv}")
    

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
                    {"nouveau_nom": nouveau_nom, "id_conv": id_conv}  
                )
                count = cursor.rowcount
        if count > 0:
            return "titre modifié avec succès"
        else:
            raise Exception(f"Erreur dans la modification du titre pour id_conv = {id_conv}")
        

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
                {"id_conv":id_conv}
                )
            count = cursor.rowcount
        if count>0:
            return(f"la conversation d'id={id_conv} a bien été supprimmée")
        else:
            return(f"echec de la suppression de la conversation d'identifiant {id_conv}")
        

    def lister_conversations(id_user: int) -> List[Conversation]:
        """
        Présente une liste des conversations reliées à un joueur.

        Parameters
        ----------
            id_user : int
                l'identifiant d'un tilisateur

        Returns
        -------
            List[Conversation]
                Renvoit une liste d'objets Conversation.

        Raises
        ------
        """
        with DBConnection().connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                """
                SELECT c.*
                FROM conversations c
                JOIN conversations_participants uc ON c.id = uc.conversation.id
                WHERE uc.utilisateur_id = %(id_user)s;
                """,
                {"id_user": id_user}
                )
                liste_DAO = cursor.fetchall()
            liste_conv = []
            if liste_DAO:
                for conv in liste_DAO:
                    liste_conv.append(Conversation(id= conv["id"], nom= conv["titre"], 
                    personnalisation = conv["prompt_id"], date_creation = conv["cree_le"]))
                return liste_conv
            else:
                raise Exception(f"aucune conversation trouvée pour l'utilisateur {id_user}")

        

    def rechercher_mot_clef(id_user: int, mot_clef: str) -> List[Conversation]:
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
        liste_CONV = lister_conversation(id_user)
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
                     {"conv_id":liste_conv,
                     "mot_clef":mot_clef}
                )
                liste = cursor.fetchall()
            liste = set(liste)
            if not liste:
                raise Exception(f"aucune conversation trouvée parmi les conversations de l'utilisateur {id_user} our le mot clé '{mot_clef}'")
            #une fois qu'on a récupéré la liste des conversations_id, on récupère les conversations 
            #depuis la table conversations (oui je sais on aurait pu fair un join mais flemme)
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT*
                    FROM conversations
                    WHERE id = ANY(%(conv_id))
                    """,
                     {"conv_id":liste}
                )
                res = cursor.fetchall()
            liste_finale = []
            for conv in res:
                liste_finale.append(Conversation(id= conv["id"], nom= conv["titre"], 
                personnalisation = conv["prompt_id"], date_creation = conv["cree_le"]))


    def rechercher_date(id_user: int, date: Date) -> List[Conversation]:
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
        #contrôle du format de la date:
        if not isinstance(date, datetime):
            raise Exception(f"la date {date} n'est pas au format datetime")

        #on récupère tous les identifiants de conversation qui ont des messages qui correspondent 
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
                    {"date":date,
                    "id_user": id_user}

                )
                dict_id = cursor.fetchall()
            if not dict_id:
                raise Exception(f"Aucune conversation de l'utilisateur {id_user} pour la date {date}")
            # on récupère 
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT *
                    FROM conversations
                    WHERE id = ANY(%(dict_id)s);
                    """,
                    {"dict_id":dict_id}
                )
                res = cursor.fetchall()
            liste_res
            for conv in res:
                liste_res.append(Conversation(id= conv["id"], nom= conv["titre"], 
                personnalisation = conv["prompt_id"], date_creation = conv["cree_le"]))
            
            return liste_res


    def lire_echanges(id_conv: int, offset: int, limit: int) -> List[Echange]:
        """
        ?.

        Parameters
        ----------
            id_conv : int
                l'identifiant du joueur
            offset : int
                ?
            limit : int
                ?
        Returns
        -------
            List[Echange]
                ?

        Raises
        ------
        """
        pass

    def rechercher_echange(id_conv: int, mot_clef: str, date: Date) -> List[Echange]:
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
        pass

    def ajouter_participant(id_conv: int, id_user: int, role: str) -> bool:
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
        pass

    def retirer_participant(id_conv: int, id_user: int) -> bool:
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
        pass

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
        pass


    def mettre_a_jopreprompt_id(id_conv: preprompt_id: str) ->bool:
        """
        Permet de changer le profil du LLM via un système de préprompt

        Parameters
        ----------
            id_conv : int
                l'identifiant de la conversation pour laquelle on veut changer le profil du LLM
preprompt_id : str
                Nom du profil du LLM à appliquer

        Returns
        -------
            Bool
                indique si le profil du LLM a été changé avec succès
        Raises
        ------
        """
        pass

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
        pass

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
        pass

    def sujets_plus_frequents(id_user: int, topK: int) -> List[str]:
        """
        Renvoie une liste des sujets les plus fréquents entretenus dans les conversations d'un utilisateur.

        Parameters
        ----------
            id_user : int
                l'identifiant de l'utilisateur dans la base de donnée
            topK : int
                ???.

        Returns
        -------
            List[str]
                Une liste des principaux sujets déterminés par le LLM

        Raises
        ------
        """
        pass
