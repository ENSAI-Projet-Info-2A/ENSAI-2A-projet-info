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
        utilisateur = self.utilisateur_dao.trouver_par_pseudo(pseudo)
        if not utilisateur:
            raise ValueError("Utilisateur introuvable.")

        if not utilisateur.verifier_password(mdp):
            raise ValueError("Mot de passe incorrect.")

        return creer_token(utilisateur.id, utilisateur.pseudo)

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
        self.tokens_invalides.add(token)

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

        if token in self.tokens_invalides:
            return False
        try:
            verif_token(token)
            return True
        except Exception:
            return False
