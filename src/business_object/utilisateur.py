import hmac
from typing import Optional

from src.utils.securite import hash_password


class Utilisateur:
    """
    Représente un utilisateur du système (Business Object).

    Cette classe encapsule les informations essentielles d'un utilisateur,
    notamment son identifiant, son pseudo, le hash de son mot de passe et les
    conversations auxquelles il participe. Elle fournit également la logique
    métier pour gérer les mots de passe (hash, vérification), et manipuler
    les conversations associées.

    Parameters
    ----------
    pseudo : str
        Nom d'utilisateur (utilisé également comme sel pour le hash du mot de passe).
    password_hash : str | None, optional
        Hash du mot de passe stocké. Peut être None lors de la création
        initiale ou si le mot de passe doit être défini plus tard.
    id : int | None, optional
        Identifiant unique de l'utilisateur (fourni par la base de données).

    Attributes
    ----------
    id : int | None
        Identifiant unique de l'utilisateur.
    pseudo : str
        Nom d'utilisateur.
    password_hash : str | None
        Hash sécurisé du mot de passe.
    conversations : list
        Liste des conversations auxquelles l'utilisateur participe.
    """

    def __init__(self, pseudo: str, password_hash: Optional[str] = None, id: Optional[int] = None):
        """
        Initialise un utilisateur avec un pseudo, un hash de mot de passe
        éventuellement fourni, et un identifiant facultatif.

        Parameters
        ----------
        pseudo : str
            Nom d'utilisateur.
        password_hash : str | None, optional
            Hash du mot de passe.
        id : int | None, optional
            Identifiant unique.
        """
        self.id = id
        self.pseudo = pseudo
        self.password_hash = password_hash
        self.conversations = []

    def afficher_utilisateur(self) -> str:
        """
        Retourne une représentation textuelle concise de l'utilisateur.

        Returns
        -------
        str
            Une chaîne contenant l'id et le pseudo.
        """
        return f"Utilisateur(id={self.id}, pseudo={self.pseudo})"

    def __str__(self):
        """Alias de `afficher_utilisateur()`."""
        return self.afficher_utilisateur()

    def __repr__(self):
        """
        Représentation technique de l'objet.

        Returns
        -------
        str
            Une chaîne du type : 'Utilisateur(id, pseudo)'.
        """
        return f"Utilisateur({self.id!r}, {self.pseudo!r})"

    def __eq__(self, other):
        """
        Vérifie l'égalité entre deux objets Utilisateur, basée sur l'id.

        Parameters
        ----------
        other : Any
            Objet à comparer.

        Returns
        -------
        bool
            True si les deux objets sont des Utilisateur avec le même id.
        """
        return isinstance(other, Utilisateur) and self.id == other.id

    # ---- Méthodes métier ----
    def set_password(self, mot_de_passe: str) -> None:
        """
        Hash et enregistre un mot de passe.

        Le mot de passe est hashé avec la fonction de sécurité utilisée
        dans les services métier : `hash_password(mot_de_passe, self.pseudo)`,
        afin de garantir une cohérence globale (sel basé sur le pseudo).

        Parameters
        ----------
        mot_de_passe : str
            Mot de passe en clair.
        """
        self.password_hash = hash_password(mot_de_passe, self.pseudo)

    def verifier_password(self, mot_de_passe: str) -> bool:
        """
        Vérifie si un mot de passe en clair correspond au hash enregistré.

        Le mot de passe fourni est re-hashé avec le même sel (`self.pseudo`)
        puis comparé au hash stocké en utilisant `hmac.compare_digest`, afin
        d'éviter les attaques par timing.

        Parameters
        ----------
        mot_de_passe : str
            Mot de passe en clair à vérifier.

        Returns
        -------
        bool
            True si le mot de passe est correct, False sinon.
        """
        if self.password_hash is None:
            return False
        expected = hash_password(mot_de_passe, self.pseudo)
        return hmac.compare_digest(self.password_hash, expected)

    def ajouter_conversation(self, conversation) -> None:
        """
        Ajoute une conversation à la liste de l'utilisateur.

        Parameters
        ----------
        conversation : Conversation
            Conversation à associer à l'utilisateur.
        """
        self.conversations.append(conversation)

    def retirer_conversation(self, conversation) -> None:
        """
        Retire une conversation de la liste si elle est présente.

        Parameters
        ----------
        conversation : Conversation
            Conversation à retirer.
        """
        if conversation in self.conversations:
            self.conversations.remove(conversation)

    def lister_conversations(self) -> list[str]:
        """
        Retourne la liste des noms des conversations de l'utilisateur.

        Returns
        -------
        list[str]
            Liste des noms (titres) des conversations.
        """
        return [conv.nom for conv in self.conversations]

    # Optionnel : constructeur pratique quand on reçoit un mdp en clair
    @classmethod
    def from_plain_password(
        cls, pseudo: str, mot_de_passe: str, id: Optional[int] = None
    ) -> "Utilisateur":
        """
        Construit un utilisateur à partir d'un mot de passe en clair.

        Cette méthode permet de créer un utilisateur puis de définir
        immédiatement un hash sécurisé pour le mot de passe.

        Parameters
        ----------
        pseudo : str
            Nom d'utilisateur.
        mot_de_passe : str
            Mot de passe en clair.
        id : int | None, optional
            Identifiant unique.

        Returns
        -------
        Utilisateur
            Nouvel utilisateur avec mot de passe hashé.
        """
        user = cls(pseudo=pseudo, password_hash=None, id=id)
        user.set_password(mot_de_passe)
        return user
