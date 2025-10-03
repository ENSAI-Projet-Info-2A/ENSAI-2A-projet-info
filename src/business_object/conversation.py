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

    def __init__(self, nom: str, personnalisation: str = "", 
                 id: int = None, date_creation: datetime = None):
        """Constructeur"""
        self.id = id
        self.nom = nom
        self.date_creation = date_creation if date_creation else datetime.now()
        self.personnalisation = personnalisation
        self.echanges = []
        self.participants = []

    def afficher_conv(self) -> str:
        """Retourne une chaîne représentant la conversation"""
        return f"Conversation(id={self.id}, nom={self.nom}, créée le {self.date_creation.strftime('%Y-%m-%d')})"

    def __str__(self):
        """Représentation sous forme de string"""
        return self.afficher_conv()

    def ajouter_participant(self, participant):
        """Ajoute un participant à la conversation"""
        self.participants.append(participant)

    def ajouter_echange(self, echange):
        """Ajoute un échange (message) à la conversation"""
        self.echanges.append(echange)
