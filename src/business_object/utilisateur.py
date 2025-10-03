import hashlib

class Utilisateur:
    """
    Classe représentant un Utilisateur (Business Object)
    """

    def __init__(self, pseudo: str, password_hash: str = None, id: int = None):
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
    def set_password(self, mot_de_passe: str):
        """Hash et enregistre un mot de passe"""
        self.password_hash = hashlib.sha256(mot_de_passe.encode()).hexdigest()

    def verifier_password(self, mot_de_passe: str) -> bool:
        """Vérifie si le mot de passe correspond au hash enregistré"""
        return self.password_hash == hashlib.sha256(mot_de_passe.encode()).hexdigest()

    def ajouter_conversation(self, conversation):
        self.conversations.append(conversation)

    def retirer_conversation(self, conversation):
        if conversation in self.conversations:
            self.conversations.remove(conversation)

    def lister_conversations(self) -> list[str]:
        return [conv.nom for conv in self.conversations]
