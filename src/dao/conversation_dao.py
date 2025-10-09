from business_object.conversation import Conversation
from business_object.echange import Echange 
from datetime import datetime as Date


class ConversationDAO:
    def __init__(titre: str, personnalisation: str, owner_id: int) -> Conversation:
        """
        Initialise une conversation.

        Parameters
        ----------
            titre : str
                le titre de la conversation
            personnalisation : str
                le nom du profil du LLM
            owner_id : int
                l'identifiant du créateur de la conversation

        """
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
        pass

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
        pass

    def supprimmer_conv(id_conv: int) -> bool:
        """
        Supprimme une conversation dans la base de donnée.

        Parameters
        ----------
            id_conv : int
                identifiant de la conversation
            
        Returns
        -------
            bool
                Indique si la conversation a été supprimée avec succès.

        Raises
        ------
        """
        pass

    def lister_conversations(id_user: int) ->List[Conversation]:
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
        pass

    def rechercher_mot_clef(id_user: int, mot_clef: str) ->List[Conversation]:
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
        pass

    def rechercher_date(id_user: int, date: Date) ->List[Conversation]:
        """
        Recherche une conversation à partir d'une date.
        -->la date de quoi ? de la création ? du dernier message ? 

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
        pass

    def lire_echanges(id_conv: int, offset: int, limit: int) ->List[Echange]:
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

    def rechercher_echange(id_conv: int, mot_clef: str, date: Date) ->List[Echange]:
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
            ExceptionType
                Description des exceptions levées (optionnel).
        """
        pass
    
    def ajouter_participant(id_conv: int, id_user: int, role: str):
        """
        Brève description de ce que fait la méthode.

        Parameters
        ----------
            param1 : Type1
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
    
    def retirer_participant(id_conv: int, id_user: int) ->bool:
        """
        Brève description de ce que fait la méthode.

        Parameters
        ----------
            param1 : Type1
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

    def ajouter_echange(id_conv: int, echange: Echange) ->bool:
        """
        Brève description de ce que fait la méthode.

        Parameters
        ----------
            param1 : Type1
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

    def mettre_a_jour_personnalisation(id_conv: int, personnalisation: str) ->bool:
        """
        Brève description de ce que fait la méthode.

        Parameters
        ----------
            param1 : Type1
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

    def compter_conversations(id_user: int) ->int:
        """
        Brève description de ce que fait la méthode.

        Parameters
        ----------
            param1 : Type1
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

    def compter_message_user(id_user: int) ->int:
        """
        Brève description de ce que fait la méthode.

        Parameters
        ----------
            param1 : Type1
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

    def sujets_plus_frequents(id_user: int, topK: int) ->List[str]:
        """
        Brève description de ce que fait la méthode.

        Parameters
        ----------
            param1 : Type1
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

    def heures_utilisation(id_user: int) ->float:
        """
        Brève description de ce que fait la méthode.

        Parameters
        ----------
            param1 : Type1
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