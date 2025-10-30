import bcrypt
import jwt 
from datetime import datetime, timedelta, timezone
from dao.utilisateur_dao import Utilisateur_DAO 
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")


class Auth_Service:
    """
    Service d'authentification pour gérer les connexions utilisateurs
    """
    def __init__(self, utilisateur_dao: Utilisateur_DAO):
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

        # Vérifie le mot de passe
        if not bcrypt.checkpw(mdp.encode(), utilisateur.password_hash.encode()):
            raise ValueError("Mot de passe incorrect.")

        # Génère un token JWT valable 1 heure
        payload = {
            "user_id": utilisateur.id,
            "pseudo": utilisateur.pseudo,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return token

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
            return False  # token déjà invalidé

        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return True
        except jwt.ExpiredSignatureError:
            print("Le token a expiré.")
            return False
        except jwt.InvalidTokenError:
            print("Token invalide.")
            return False
