from InquirerPy import inquirer

from src.service.utilisateur_service import UtilisateurService
from src.view.session import Session
from src.view.vue_abstraite import VueAbstraite


class ConnexionVue(VueAbstraite):
    """Vue de Connexion (saisie de pseudo et mot de passe)"""

    def choisir_menu(self):
        # Demande à l'utilisateur de saisir pseudo et mot de passe

        pseudo = inquirer.text(message="Entrez votre pseudo : ").execute()
        mdp = inquirer.secret(message="Entrez votre mot de passe :").execute()

        # Appel du service pour trouver l'utilisateur
        utilisateur = UtilisateurService().se_connecter(pseudo, mdp)

        # Si l'utilisateur a été trouvé à partir de ses identifiants de connexion
        if utilisateur:
            message = f"Vous êtes connecté sous le pseudo {utilisateur.pseudo}"
            Session().connexion(utilisateur)
            from view.menu_utilisateur_vue import MenuUtilisateurVue

            return MenuUtilisateurVue(message)

        message = "Erreur de connexion (pseudo ou mot de passe invalide)"
        from src.view.accueil.accueil_vue import AccueilVue

        return AccueilVue(message)
