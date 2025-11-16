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
        self,
        message: str,
        agent: str = "utilisateur",
        agent_name: str = "",
        id: int = None,
        date_msg: datetime = None,
    ):
        """
        Initialise un nouvel échange.

        Parameters
        ----------
        message : str
            Contenu textuel du message.
        agent : str, optional
            Type d'émetteur de l’échange.
        agent_name : str, optional
            Nom affiché de l’émetteur.
        id : int, optional
            Identifiant unique de l’échange.
        date_msg : datetime, optional
            Date et heure d’envoi.
        """
        self.id = id
        self.agent = agent
        self.message = message
        self.agent_name = agent_name
        self.date_msg = date_msg if date_msg else datetime.now()

    def afficher_echange(self) -> str:
        """
        Retourne une chaîne lisible représentant l'échange.

        Returns
        -------
        str
            Chaîne formatée de la forme :
            `"[AAAA-MM-JJ HH:MM:SS] agent: message"`.
        """
        return f"[{self.date_msg.strftime('%Y-%m-%d %H:%M:%S')}] {self.agent_name or self.agent}: {self.message}"

    def __str__(self):
        """
        Représentation textuelle par défaut de l'objet Echange.

        Returns
        -------
        str
            Une chaîne produite par `afficher_echange()`.
        """
        return self.afficher_echange()
