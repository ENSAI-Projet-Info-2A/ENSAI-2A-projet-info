from datetime import datetime


class Echange:
    """
    Classe représentant un échange (message) dans une conversation

    Attributs
    ----------
    id : int
        identifiant unique de l'échange
    agent : str
        identifiant ou type d'agent (ex: "utilisateur", "machine")
    message : str
        contenu du message
    date_msg : datetime
        date et heure de l'envoi du message
    """

    def __init__(
        self, message: str, agent: str = "utilisateur", id: int = None, date_msg: datetime = None
    ):
        self.id = id
        self.agent = agent
        self.message = message
        self.date_msg = date_msg if date_msg else datetime.now()

    def afficher_echange(self) -> str:
        """Retourne une chaîne représentant l'échange"""
        return f"[{self.date_msg.strftime('%Y-%m-%d %H:%M:%S')}] {self.agent_name or self.agent}: {self.message}"

    def __str__(self):
        """Représentation sous forme de string"""
        return self.afficher_echange()
