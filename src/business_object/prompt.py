# Cette classe est inutiles dans notre projet, mais si on voulait pousser plus loin le système de 
# promt, elle serait dans le futur nécessaire.

class Prompt:
    """
    Classe représentant un prompt système / personnalisé.

    Cette classe correspond à la table `prompts` de la base de données.

    Attributs
    ----------
    id : int | None
        Identifiant unique du prompt en base de données.
    nom : str
        Nom fonctionnel du prompt (ex: "default", "fr_strict_v2", etc.).
    contenu : str
        Texte complet du prompt (pré-prompt utilisé pour initialiser l'IA).
    version : int
        Numéro de version du prompt.
    """

    def __init__(
        self,
        nom: str,
        contenu: str,
        version: int = 1,
        id: int | None = None,
    ):
        """
        Initialise un objet Prompt.

        Parameters
        ----------
        nom : str
            Nom du prompt (unique dans la base).
        contenu : str
            Contenu textuel du prompt.
        version : int, optional
            Numéro de version, par défaut 1.
        id : int | None, optional
            Identifiant en base (None si le prompt n'est pas encore enregistré).
        """
        self.id = id
        self.nom = nom
        self.contenu = contenu
        self.version = version

    def __repr__(self) -> str:
        """
        Représentation non-ambiguë de l'objet, utile pour le debug.
        """
        return f"Prompt(id={self.id!r}, nom={self.nom!r}, version={self.version!r})"

    def apercu(self, longueur: int = 50) -> str:
        """
        Retourne un aperçu court du contenu du prompt.

        Parameters
        ----------
        longueur : int, optional
            Longueur maximale de l'aperçu.

        Returns
        -------
        str
            Début du contenu suivi de "..." si tronqué.
        """
        if len(self.contenu) <= longueur:
            return self.contenu
        return self.contenu[: longueur - 3] + "..."
