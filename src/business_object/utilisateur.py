class Utilisateur:
    """
    Classe représentant un Utilisateur

    Attributs
    ----------
    id_utilisateur : int
        identifiant
    pseudo : str
        pseudo de l'utilisateur
    mdp : str
        le mot de passe de l'utilisateur
    age : int
        age de l'utilisateur
    mail : str
        mail de l'utilisateur
    """

    def __init__(self, pseudo, age, mail, mdp=None, id_utilisateur=None):
        """Constructeur"""
        self.id_utilisateur = id_utilisateur
        self.pseudo = pseudo
        self.mdp = mdp
        self.age = age
        self.mail = mail

    def __str__(self):
        """Permet d'afficher les informations de l'utilisateur"""
        return f"Utilisateur({self.pseudo}, {self.age} ans)"

    def as_list(self) -> list[str]:
        """Retourne les attributs de l'utilisateur dans une liste"""
        return [self.pseudo, self.age, self.mail]
