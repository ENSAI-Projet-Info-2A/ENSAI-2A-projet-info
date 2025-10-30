from utils.log_decorator import log
from utils.securite import hash_password

from business_object.utilisateur import Utilisateur
from dao.utilisateur_dao import UtilisateurDao
import hmac # Pour de la sécurité


class UtilisateurService:
    @staticmethod
    def _norm_pseudo(pseudo: str | None) -> str | None:
        "Fonction qui normalise les pseudos pour éviter les problèmes"
        if pseudo is None:
            return None
        p = pseudo.strip()
        # p = p.lower() 
        return p or None

    @log
    def creer_compte(self, pseudo: str, mdp: str) -> Utilisateur | None:
        pseudo_n = self._norm_pseudo(pseudo)
        if not pseudo_n or not mdp:
            return None
        if self.pseudo_deja_utilise(pseudo_n):
            return None

        user = Utilisateur(id=None, pseudo=pseudo_n,
                           password_hash=hash_password(mdp, pseudo_n))
        created = UtilisateurDao().creer(user)
        return created if isinstance(created, Utilisateur) else (user if created else None)

    @log
    def trouver_par_id(self, user_id: int) -> Utilisateur | None:
        return UtilisateurDao().trouver_par_id(user_id)

    @log
    def trouver_par_pseudo(self, pseudo: str) -> Utilisateur | None:
        pseudo_n = self._norm_pseudo(pseudo)
        return None if not pseudo_n else UtilisateurDao().trouver_par_pseudo(pseudo_n)

    @log
    def lister_tous(self, inclure_hash: bool = False) -> list[Utilisateur]:
        users = UtilisateurDao().lister_tous()
        if inclure_hash:
            return users
        # renvoyer des copies pour ne pas écraser les objets originaux (On ne sait jamais)
        return [Utilisateur(id=u.id, pseudo=u.pseudo, password_hash=None) for u in users]

    @log
    def supprimer(self, utilisateur: Utilisateur) -> bool:
        return UtilisateurDao().supprimer(utilisateur)

    @log
    def pseudo_deja_utilise(self, pseudo: str) -> bool:
        pseudo_n = self._norm_pseudo(pseudo)
        return False if not pseudo_n else (UtilisateurDao().trouver_par_pseudo(pseudo_n) is not None)

    @log
    def se_connecter(self, pseudo: str, mdp: str) -> Utilisateur | None:
        pseudo_n = self._norm_pseudo(pseudo)
        if not pseudo_n or not mdp:
            return None
        u = UtilisateurDao().trouver_par_pseudo(pseudo_n)
        if not u or not u.password_hash:
            return None
        expected = hash_password(mdp, pseudo_n)
        return u if hmac.compare_digest(u.password_hash, expected) else None