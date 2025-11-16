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
        """
        Initialise un participant appartenant à une conversation.

        Parameters
        ----------
        user_id : int
            Identifiant de l'utilisateur.
        conv_id : int
            Identifiant de la conversation.
        role : str, optional
            Rôle attribué au participant.
        date_joined : datetime, optional
            Date d’entrée dans la conversation.
        """
        self.user_id = user_id
        self.conv_id = conv_id
        self.role = role
        self.date_joined = date_joined if date_joined else datetime.now()

    def afficher_participant(self) -> str:
        """
        Retourne une chaîne décrivant le participant.

        Returns
        -------
        str
            Chaîne de la forme :
            `"Participant(user_id=..., conv_id=..., role=..., date_joined=...)"`.
        """
        return f"Participant(user_id={self.user_id}, conv_id={self.conv_id}, role={self.role}, date_joined={self.date_joined})"

    def __str__(self):
        """
        Représentation textuelle par défaut du participant.

        Returns
        -------
        str
            Résultat de `afficher_participant()`.
        """
        return self.afficher_participant()
