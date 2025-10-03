class Auth_Service:
    """
    Service d'authentification pour gérer les connexions utilisateurs
    """

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
        pass

    def se_deconnecter(self, token: str) -> None:
        """
        Déconnecte un utilisateur en invalidant son token.

        Parameters
        ----------
        token : str
            Token de session à invalider
        """
        pass

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
        pass
