import hmac
from typing import Optional

from utils.securite import hash_password


class Utilisateur:
    """
    Classe représentant un Utilisateur (Business Object)
    """

    def __init__(self, pseudo: str, password_hash: Optional[str] = None, id: Optional[int] = None):
        self.id = id
        self.pseudo = pseudo
        self.password_hash = password_hash
        self.conversations = []

    def afficher_utilisateur(self) -> str:
        return f"Utilisateur(id={self.id}, pseudo={self.pseudo})"

    def __str__(self):
        return self.afficher_utilisateur()

    def __repr__(self):
        return f"Utilisateur({self.id!r}, {self.pseudo!r})"

    def __eq__(self, other):
        return isinstance(other, Utilisateur) and self.id == other.id

    # ---- Méthodes métier ----
    def set_password(self, mot_de_passe: str) -> None:
        """
        Hash et enregistre un mot de passe avec la même fonction que le service.
        On utilise `hash_password(mot_de_passe, self.pseudo)` pour rester cohérent.
        """
        self.password_hash = hash_password(mot_de_passe, self.pseudo)

    def verifier_password(self, mot_de_passe: str) -> bool:
        """
        Vérifie si le mot de passe correspond au hash enregistré.
        Re-hash le mot de passe saisi avec le même sel (pseudo)
        et compare en temps constant avec hmac.
        """
        if self.password_hash is None:
            return False
        expected = hash_password(mot_de_passe, self.pseudo)
        return hmac.compare_digest(self.password_hash, expected)

    def ajouter_conversation(self, conversation) -> None:
        self.conversations.append(conversation)

    def retirer_conversation(self, conversation) -> None:
        if conversation in self.conversations:
            self.conversations.remove(conversation)

    def lister_conversations(self) -> list[str]:
        return [conv.nom for conv in self.conversations]

    # Optionnel : constructeur pratique quand on reçoit un mdp en clair
    @classmethod
    def from_plain_password(
        cls, pseudo: str, mot_de_passe: str, id: Optional[int] = None
    ) -> "Utilisateur":
        user = cls(pseudo=pseudo, password_hash=None, id=id)
        user.set_password(mot_de_passe)
        return user
