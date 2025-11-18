import logging

from InquirerPy import inquirer

from src.dao.utilisateur_dao import UtilisateurDao
from src.service.auth_service import Auth_Service
from src.service.utilisateur_service import UtilisateurService
from src.view.session import Session
from src.view.vue_abstraite import VueAbstraite


class ConnexionVue(VueAbstraite):
    """Vue de Connexion (saisie de pseudo et mot de passe)."""

    def __init__(self, message: str = ""):
        self.message = message

    def choisir_menu(self):
        if self.message:
            print(self.message + "\n")

        # 1) Saisie des identifiants
        pseudo = inquirer.text(message="Entrez votre pseudo : ").execute()
        mdp = inquirer.secret(message="Entrez votre mot de passe :").execute()

        auth_service = Auth_Service(UtilisateurDao())

        try:
            # 2) Authentification + token JWT
            token = auth_service.se_connecter(pseudo, mdp)
        except ValueError as e:
            logging.warning(f"[ConnexionVue] Erreur d'authentification : {e}")
            from src.view.accueil.accueil_vue import AccueilVue

            return AccueilVue("Erreur de connexion (pseudo ou mot de passe invalide)")

        # 3) Récupérer l'objet Utilisateur pour la session CLI
        utilisateur = UtilisateurService().trouver_par_pseudo(pseudo)

        if not utilisateur:
            logging.error(
                "[ConnexionVue] Utilisateur authentifié mais non trouvé par UtilisateurService"
            )
            from src.view.accueil.accueil_vue import AccueilVue

            return AccueilVue("Erreur interne : utilisateur authentifié mais non trouvé.")

        # 4) On ouvre la session locale + BDD
        Session().connexion(utilisateur, token=token)

        message = f"Vous êtes connecté sous le pseudo {utilisateur.pseudo}"

        from src.view.menu_utilisateur_vue import MenuUtilisateurVue

        return MenuUtilisateurVue(message)
