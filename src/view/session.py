from datetime import datetime

from src.dao.session_dao import SessionDAO
from src.utils.singleton import Singleton


class Session(metaclass=Singleton):
    """Stocke l'état local + journalise en base via SessionDAO."""

    def __init__(self):
        self.utilisateur = None
        self.debut_connexion = None
        self.session_db_id = None
        self.token = None

    def connexion(self, utilisateur, token: str | None = None):
        """Enregistre la session et crée la ligne en base."""
        self.utilisateur = utilisateur
        self.debut_connexion = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        try:
            self.session_db_id = SessionDAO().ouvrir(utilisateur.id)
        except Exception:
            # On ne casse pas l'UX si la BDD plante : on loguera côté main
            self.session_db_id = None
        self.token = token

    def deconnexion(self):
        """Ferme la session locale + met à jour la BDD si possible."""
        try:
            if self.utilisateur:
                SessionDAO().fermer_derniere_ouverte(self.utilisateur.id)
        finally:
            self.utilisateur = None
            self.debut_connexion = None
            self.session_db_id = None
            self.token = None

    def afficher(self) -> str:
        res = "Actuellement en session :\n"
        res += "-------------------------\n"
        res += f"utilisateur : {getattr(self.utilisateur, 'pseudo', None)}\n"
        res += f"debut_connexion : {self.debut_connexion}\n"
        res += f"session_db_id : {self.session_db_id}\n"
        return res
