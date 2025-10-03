from datetime import datetime

class Participant:
    """
    Classe représentant un participant à une conversation

    Attributs
    ----------
    user_id : int
        identifiant de l'utilisateur
    conv_id : int
        identifiant de la conversation
    role : str
        rôle du participant (ex: "admin", "membre")
    date_joined : datetime
        date d'entrée dans la conversation
    """

    def __init__(self, user_id: int, conv_id: int, role: str = "membre", date_joined: datetime = None):
        """Constructeur"""
        self.user_id = user_id
        self.conv_id = conv_id
        self.role = role
        self.date_joined = date_joined if date_joined else datetime.now()

    def afficher_participant(self) -> str:
        """Retourne une chaîne représentant le participant"""
        return f"Participant(user_id={self.user_id}, conv_id={self.conv_id}, role={self.role}, date_joined={self.date_joined})"

    def __str__(self):
        """Représentation sous forme de string"""
        return self.afficher_participant()
