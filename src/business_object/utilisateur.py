class Utilisateur:
    """
    Classe représentant un Utilisateur

    Attributs
    ----------
    id : int
        identifiant unique de l'utilisateur
    pseudo : str
        pseudo de l'utilisateur
    password_hash : str
        mot de passe hashé de l'utilisateur
    conversations : list
        liste des conversations de l'utilisateur
    """

    def __init__(self, pseudo: str, password_hash: str, id: int = None):
        """Constructeur"""
        self.id = id
        self.pseudo = pseudo
        self.password_hash = password_hash
        self.conversations = []

    def afficher_utilisateur(self) -> str:
        """Retourne une chaîne représentant l'utilisateur"""
        return f"Utilisateur(id={self.id}, pseudo={self.pseudo})"

    def __str__(self):
        """Représentation sous forme de string"""
        return self.afficher_utilisateur()

    def ajouter_conversation(self, conversation):
        """Ajoute une conversation à la liste de l'utilisateur"""
        self.conversations.append(conversation)