import logging

from src.dao.utilisateur_dao import UtilisateurDao
from src.utils.jtw_utils import creer_token
from src.utils.jtw_utils import verifier_token as verif_token


class Auth_Service:
    """
    Service d'authentification pour la gestion des connexions utilisateurs.

    Ce service encapsule la logique métier liée à l'authentification :
    - Connexion / vérification du mot de passe
    - Génération de tokens JWT
    - Gestion des tokens invalidés (déconnexion)

    Attributes
    ----------
    utilisateur_dao : UtilisateurDao
        DAO permettant d'accéder aux utilisateurs en base.
    tokens_invalides : set[str]
        Ensemble des tokens invalidés après déconnexion.
    """

    def __init__(self, utilisateur_dao: UtilisateurDao):
        """
        Initialise le service avec un DAO utilisateur.

        Parameters
        ----------
        utilisateur_dao : UtilisateurDao
            Instance du DAO pour accéder aux utilisateurs.
        """
        self.utilisateur_dao = utilisateur_dao
        self.tokens_invalides = set()  # liste noire des tokens déconnectés
        logging.debug("Initialisation Auth_Service avec UtilisateurDao=%r", utilisateur_dao)

    def se_connecter(self, pseudo: str, mdp: str) -> str:
        """
        Authentifie un utilisateur avec son pseudo et mot de passe.

        Si les identifiants sont corrects, renvoie un token JWT unique
        pour la session.

        Parameters
        ----------
        pseudo : str
            Pseudo de l'utilisateur
        mdp : str
            Mot de passe en clair

        Returns
        -------
        str
            Token de session (JWT) valide

        Raises
        ------
        ValueError
            Si l'utilisateur n'existe pas ou si le mot de passe est incorrect.
        """
        logging.debug("Tentative de connexion pour pseudo=%r", pseudo)

        utilisateur = self.utilisateur_dao.trouver_par_pseudo(pseudo)
        if not utilisateur:
            logging.warning("Connexion échouée : utilisateur %r introuvable.", pseudo)
            raise ValueError("Utilisateur introuvable.")

        if not utilisateur.verifier_password(mdp):
            logging.warning("Connexion échouée : mot de passe incorrect pour pseudo=%r", pseudo)
            raise ValueError("Mot de passe incorrect.")

        token = creer_token(utilisateur.id, utilisateur.pseudo)
        logging.info("Connexion réussie pour pseudo=%r (id=%s)", utilisateur.pseudo, utilisateur.id)
        return token

    def se_deconnecter(self, token: str) -> None:
        """
        Déconnecte un utilisateur en invalidant son token.

        L'ajout du token dans la liste noire empêche toute utilisation
        ultérieure de ce token pour accéder aux ressources protégées.

        Parameters
        ----------
        token : str
            Token de session à invalider
        """
        logging.debug("Demande de déconnexion pour token commençant par %r", token[:10])
        self.tokens_invalides.add(token)
        logging.info(
            "Token ajouté à la liste noire (nb_tokens_invalides=%s)", len(self.tokens_invalides)
        )

    def verifier_token(self, token: str) -> bool:
        """
        Vérifie la validité d'un token JWT.

        Un token est considéré valide si :
        - il n'est pas dans la liste noire des tokens invalidés
        - sa signature et sa date d'expiration sont correctes

        Parameters
        ----------
        token : str
            Token de session à vérifier

        Returns
        -------
        bool
            True si le token est valide et actif, False sinon
        """
        logging.debug(
            "Vérification du token (liste noire contient %s token(s))",
            len(self.tokens_invalides),
        )

        if token in self.tokens_invalides:
            logging.info("Token rejeté : présent dans la liste noire.")
            return False
        try:
            verif_token(token)
            logging.debug("Token valide et non expiré.")
            return True
        except Exception:
            logging.warning("Token invalide ou expiré.")
            return False
