from utils.log_decorator import log
from utils.securite import hash_password

from business_object.utilisateur import Utilisateur
from dao.utilisateur_dao import UtilisateurDao


class UtilisateurService:
    """Méthodes métier pour Utilisateur"""

    @log
    def creer_compte(self, pseudo: str, mdp: str) -> Utilisateur | None:
        # Unicité du pseudo côté service (défense en profondeur)
        if self.pseudo_deja_utilise(pseudo):
            return None

        user = Utilisateur(
            id=None,
            pseudo=pseudo,
            password_hash=hash_password(mdp, pseudo),
        )
        return user if UtilisateurDao().creer(user) else None

    @log
    def trouver_par_id(self, user_id: int) -> Utilisateur | None:
        return UtilisateurDao().trouver_par_id(user_id)

    @log
    def trouver_par_pseudo(self, pseudo: str) -> Utilisateur | None:
        return UtilisateurDao().trouver_par_pseudo(pseudo)

    @log
    def lister_tous(self, inclure_hash: bool = False) -> list[Utilisateur]:
        users = UtilisateurDao().lister_tous()
        if not inclure_hash:
            for u in users:
                u.password_hash = None  # masquage par défaut
        return users

    @log
    def supprimer(self, utilisateur: Utilisateur) -> bool:
        return UtilisateurDao().supprimer(utilisateur)

    @log
    def pseudo_deja_utilise(self, pseudo: str) -> bool:
        return UtilisateurDao().trouver_par_pseudo(pseudo) is not None

    @log
    def se_connecter(self, pseudo: str, mdp: str) -> Utilisateur | None:
        """Renvoie l'utilisateur si le couple (pseudo, mdp) est valide"""
        u = UtilisateurDao().trouver_par_pseudo(pseudo)
        if not u:
            return None
        return u if u.password_hash == hash_password(mdp, pseudo) else None