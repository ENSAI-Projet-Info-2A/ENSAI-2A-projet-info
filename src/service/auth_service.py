import os

from dotenv import load_dotenv

from src.business_object.utilisateur import verifier_password
from src.dao.utilisateur_dao import UtilisateurDAO
from src.utils.jtw_utils import creer_token
from src.utils.jtw_utils import verifier_token as verif_token

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")


class Auth_Service:
    """
    Service d'authentification pour gérer les connexions utilisateurs
    """

    def __init__(self, utilisateur_dao: UtilisateurDAO):
        """
        Initialise le service d'authentification avec un DAO utilisateur.

        Parameters
        ----------
        utilisateur_dao : UtilisateurDAO
            Instance du DAO permettant d'accéder aux utilisateurs.
        """
        self.utilisateur_dao = utilisateur_dao
        self.tokens_invalides = set()  # liste noire des tokens déconnectés

    def se_connecter(self, pseudo: str, mdp: str) -> str:
        """
        Authentifie un utilisateur avec son pseudo et mot de passe.
        Retourne un token de session si succès.

        Parameters
        ----------
        pseudo : str
            Pseudo de l'utilisateur
        mdp : str
            Mot de passe en clair

        Returns
        -------
        str
            Token de session
        """
        utilisateur = self.utilisateur_dao.trouver_par_pseudo(pseudo)
        if not utilisateur:
            raise ValueError("Utilisateur introuvable.")

        if not verifier_password(mdp, utilisateur.password_hash):
            raise ValueError("Mot de passe incorrect.")

        return creer_token(utilisateur.id, utilisateur.pseudo)

    def se_deconnecter(self, token: str) -> None:
        """
        Déconnecte un utilisateur en invalidant son token.

        Parameters
        ----------
        token : str
            Token de session à invalider
        """
        self.tokens_invalides.add(token)

    def verifier_token(self, token: str) -> bool:
        """
        Vérifie si un token est valide.

        Parameters
        ----------
        token : str
            Token de session

        Returns
        -------
        bool
            True si le token est valide, False sinon
        """

        if token in self.tokens_invalides:
            return False
        try:
            verif_token(token)
            return True
        except Exception:
            return False
