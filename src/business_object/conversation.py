from datetime import datetime


class Conversation:
    """
    Classe représentant une conversation

    Attributs
    ----------
    id : int
        identifiant unique de la conversation
    nom : str
        nom de la conversation
    date_creation : datetime
        date de création de la conversation
    personnalisation : str
        paramètres de personnalisation, préprompte # [Peut être modifier plus tard la forme]
    echanges : list
        liste des échanges (messages) dans la conversation
    participants : list
        liste des participants de la conversation
    """

    def __init__(
        self,
        nom: str,
        personnalisation: str | int | None = None,
        id: int | None = None,
        date_creation: datetime | None = None,
        proprietaire_id: int | None = None,
    ):
        """
        Constructeur de la classe Conversation.

        Initialise l'objet avec un nom obligatoire, et des valeurs optionnelles
        pour l’identifiant, la personnalisation et la date de création.

        Parameters
        ----------
        nom : str
            Nom de la conversation.
        personnalisation : str | int | None, optional
            Paramètres de personnalisation du comportement de l’IA.
        id : int, optional
            Identifiant unique (si conversation déjà existante en base).
        proprietaire_id : int | None, optional
            Identifiant du propriétaire de la conversation.
        date_creation : datetime, optional
            Date de création ; par défaut la date et l'heure actuelles.
        """
        self.id = id
        self.nom = nom
        self.proprietaire_id = proprietaire_id
        self.date_creation = date_creation if date_creation else datetime.now()
        self.personnalisation = personnalisation
        self.echanges = []
        self.participants = []

    def afficher_conv(self) -> str:
        """
        Retourne une représentation lisible et courte de la conversation.

        Returns
        -------
        str
            Chaîne de la forme :
            `"Conversation(id=..., nom=..., créée le YYYY-MM-DD)"`.
        """
        return f"Conversation(id={self.id}, nom={self.nom}, créée le {self.date_creation.strftime('%Y-%m-%d')})"

    def __str__(self):
        """
        Représentation textuelle par défaut de l'objet Conversation.

        Returns
        -------
        str
            Résultat de : `self.afficher_conv()`.
        """
        return self.afficher_conv()

    def ajouter_participant(self, participant):
        """
        Ajoute un participant à la conversation.

        Parameters
        ----------
        participant : Any
            Participant à ajouter. Généralement un objet Utilisateur
            ou un identifiant d'utilisateur.

        Returns
        -------
        None
        """
        self.participants.append(participant)

    def ajouter_echange(self, echange):
        """
        Ajoute un échange (message) à la conversation.

        Parameters
        ----------
        echange : Echange
            Objet représentant un message envoyé par l’utilisateur ou l’IA.

        Returns
        -------
        None
        """
        self.echanges.append(echange)
