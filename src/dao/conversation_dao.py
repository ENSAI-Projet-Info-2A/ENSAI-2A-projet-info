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
            ExceptionType
                Description des exceptions levées (optionnel).
        """
        pass

    def lister_conversations(id_user: int) ->List[Conversation]:
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

    def rechercher_mot_clef(id_user: int, mot_clef: str) ->List[Conversation]:
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

    def rechercher_date(id_user: int, date: Date) ->List[Conversation]:
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

    def lire_echanges(id_conv: int, offset: int, limit: int) ->List[Echange]:
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

    def rechercher_echange(id_conv: int, mot_clef, date: Date) ->List[Echange]:
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