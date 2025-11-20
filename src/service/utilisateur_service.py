import logging

from src.business_object.utilisateur import Utilisateur
from src.dao.utilisateur_dao import UtilisateurDao
from src.utils.log_decorator import log
from src.utils.securite import hash_password


class UtilisateurService:
    """
    Service de gestion des utilisateurs.

    Cette classe fournit des méthodes pour créer, retrouver, lister et supprimer
    des utilisateurs, ainsi que pour vérifier la disponibilité des pseudos
    et gérer l'authentification.

    Méthodes :
    ----------
    _norm_pseudo(pseudo: str | None) -> str | None
        Normalise un pseudo en supprimant les espaces inutiles et en convertissant
        en minuscules. Retourne None si le pseudo est vide ou None.

    creer_compte(pseudo: str, mdp: str) -> Utilisateur | None
        Crée un nouvel utilisateur avec un pseudo et un mot de passe.
        Retourne l'utilisateur créé ou None si le pseudo est déjà utilisé
        ou si les données sont invalides.

    trouver_par_id(user_id: int) -> Utilisateur | None
        Retourne l'utilisateur correspondant à l'identifiant fourni,
        ou None si aucun utilisateur n'est trouvé.

    trouver_par_pseudo(pseudo: str) -> Utilisateur | None
        Retourne l'utilisateur correspondant au pseudo fourni après normalisation,
        ou None si aucun utilisateur n'est trouvé.

    lister_tous(inclure_hash: bool = False) -> list[Utilisateur]
        Retourne la liste de tous les utilisateurs.
        Si inclure_hash est False, les mots de passe sont masqués (None).

    supprimer(utilisateur: Utilisateur) -> bool
        Supprime l'utilisateur fourni de la base de données.
        Retourne True si la suppression a réussi, False sinon.

    pseudo_deja_utilise(pseudo: str) -> bool
        Vérifie si un pseudo est déjà utilisé.
        Retourne True si le pseudo existe déjà, False sinon.

    se_connecter(pseudo: str, mdp: str) -> Utilisateur | None
        Authentifie un utilisateur avec un pseudo et un mot de passe.
        Retourne l'utilisateur si l'authentification réussit, None sinon.
    """

    @staticmethod
    def _norm_pseudo(pseudo: str | None) -> str | None:
        """
        Normalise un pseudo.

        Supprime les espaces inutiles et convertit en minuscules pour éviter
        les doublons dus à la casse ou aux espaces.

        Parameters:
        -----------
        pseudo : str | None
            Le pseudo à normaliser.

        Returns:
        --------
        str | None
            Le pseudo normalisé ou None si le pseudo est vide ou None.
        """
        logging.debug("Normalisation du pseudo %r", pseudo)

        if pseudo is None:
            return None
        p = pseudo.strip()
        p = p.lower()
        return p or None

    @log
    def creer_compte(self, pseudo: str, mdp: str) -> Utilisateur | None:
        """
        Crée un compte utilisateur.

        Vérifie que le pseudo n'est pas déjà utilisé et que les données sont valides,
        puis crée un utilisateur avec un mot de passe hashé.

        Parameters:
        -----------
        pseudo : str
            Le pseudo choisi pour le compte.
        mdp : str
            Le mot de passe du compte.

        Returns:
        --------
        Utilisateur | None
            L'utilisateur créé si la création réussit, sinon None.
        """
        pseudo_n = self._norm_pseudo(pseudo)
        if not pseudo_n or not mdp:
            logging.warning(
                "Échec création compte : pseudo ou mot de passe invalide (pseudo=%r).",
                pseudo,
            )
            return None
        if self.pseudo_deja_utilise(pseudo_n):
            logging.info("Échec création compte : pseudo déjà utilisé (%r).", pseudo_n)
            return None

        user = Utilisateur(id=None, pseudo=pseudo_n, password_hash=hash_password(mdp, pseudo_n))
        created = UtilisateurDao().creer_utilisateur(user)

        if isinstance(created, Utilisateur):
            logging.info("Compte utilisateur créé (id=%s, pseudo=%r).", created.id, created.pseudo)
        elif created:
            logging.info("Compte utilisateur créé (sans objet retourné, pseudo=%r).", pseudo_n)
        else:
            logging.warning("Échec création compte pour pseudo=%r sans message d'erreur.", pseudo_n)

        return created if isinstance(created, Utilisateur) else (user if created else None)

    @log
    def trouver_par_id(self, user_id: int) -> Utilisateur | None:
        """
        Trouve un utilisateur par son ID.

        Parameters:
        -----------
        user_id : int
            L'identifiant unique de l'utilisateur.

        Returns:
        --------
        Utilisateur | None
            L'utilisateur correspondant, ou None si non trouvé.
        """
        return UtilisateurDao().trouver_par_id(user_id)

    @log
    def trouver_par_pseudo(self, pseudo: str) -> Utilisateur | None:
        """
        Trouve un utilisateur par son pseudo.

        Parameters:
        -----------
        pseudo : str
            Le pseudo de l'utilisateur.

        Returns:
        --------
        Utilisateur | None
            L'utilisateur correspondant, ou None si non trouvé.
        """
        pseudo_n = self._norm_pseudo(pseudo)
        return None if not pseudo_n else UtilisateurDao().trouver_par_pseudo(pseudo_n)

    @log
    def lister_tous(self, inclure_hash: bool = False) -> list[Utilisateur]:
        """
        Liste tous les utilisateurs.

        Parameters:
        -----------
        inclure_hash : bool
            Indique si le hash du mot de passe doit être inclus dans la liste.

        Returns:
        --------
        list[Utilisateur]
            Liste des utilisateurs.
        """
        users = UtilisateurDao().lister_tous()
        if inclure_hash:
            logging.info("Liste des utilisateurs récupérée (nb=%s, avec hash).", len(users))
            return users
        # renvoyer des copies pour ne pas écraser les objets originaux (On ne sait jamais)
        logging.info("Liste des utilisateurs récupérée (nb=%s, hash masqué).", len(users))
        return [Utilisateur(id=u.id, pseudo=u.pseudo, password_hash=None) for u in users]

    @log
    def supprimer(self, utilisateur: Utilisateur) -> bool:
        """
        Supprime un utilisateur.

        Parameters:
        -----------
        utilisateur : Utilisateur
            L'utilisateur à supprimer.

        Returns:
        --------
        bool
            True si la suppression a réussi, False sinon.
        """
        resultat = UtilisateurDao().supprimer(utilisateur)
        if resultat:
            logging.info(
                "Utilisateur supprimé (id=%s, pseudo=%r).", utilisateur.id, utilisateur.pseudo
            )
        else:
            logging.warning(
                "Échec suppression utilisateur (id=%s, pseudo=%r).",
                getattr(utilisateur, "id", None),
                getattr(utilisateur, "pseudo", None),
            )
        return resultat

    @log
    def pseudo_deja_utilise(self, pseudo: str) -> bool:
        """
        Vérifie si un pseudo est déjà utilisé.

        Parameters:
        -----------
        pseudo : str
            Le pseudo à vérifier.

        Returns:
        --------
        bool
            True si le pseudo est déjà utilisé, False sinon.
        """
        pseudo_n = self._norm_pseudo(pseudo)
        existe = (
            False if not pseudo_n else (UtilisateurDao().trouver_par_pseudo(pseudo_n) is not None)
        )
        logging.debug("Vérification pseudo déjà utilisé (%r) -> %s", pseudo_n, existe)
        return existe

    @log
    def se_connecter(self, pseudo: str, mdp: str) -> Utilisateur | None:
        """
        Authentifie un utilisateur.

        Vérifie le pseudo et le mot de passe. Retourne l'utilisateur si
        l'authentification réussit.

        Parameters:
        -----------
        pseudo : str
            Le pseudo de l'utilisateur.
        mdp : str
            Le mot de passe de l'utilisateur.

        Returns:
        --------
        Utilisateur | None
            L'utilisateur authentifié, ou None si l'authentification échoue.
        """
        pseudo_n = self._norm_pseudo(pseudo)
        if not pseudo_n or not mdp:
            logging.warning(
                "Tentative de connexion avec données invalides (pseudo=%r).",
                pseudo,
            )
            return None

        u = UtilisateurDao().trouver_par_pseudo(pseudo_n)
        if not u:
            logging.info("Connexion échouée : utilisateur %r introuvable.", pseudo_n)
            return None

        if u.verifier_password(mdp):
            logging.info("Connexion réussie pour pseudo=%r (id=%s).", u.pseudo, u.id)
            return u

        logging.info("Connexion échouée : mot de passe incorrect pour pseudo=%r.", pseudo_n)
        return None
