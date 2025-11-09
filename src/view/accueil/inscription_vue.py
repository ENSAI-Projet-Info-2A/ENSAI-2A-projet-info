from InquirerPy import inquirer
from InquirerPy.validator import PasswordValidator

from src.service.utilisateur_service import UtilisateurService
from src.view.vue_abstraite import VueAbstraite


class InscriptionVue(VueAbstraite):
    """Vue d'inscription d'un nouvel utilisateur"""

    def choisir_menu(self):
        # Demande à l'utilisateur de saisir un pseudo
        pseudo = inquirer.text(message="Entrez votre pseudo : ").execute()

        # Vérifie si le pseudo est déjà utilisé
        if UtilisateurService().pseudo_deja_utilise(pseudo):
            from src.view.accueil.accueil_vue import AccueilVue

            return AccueilVue(f"Le pseudo {pseudo} est déjà utilisé.")

        # Demande à l'utilisateur de saisir un mot de passe
        mdp = inquirer.secret(
            message="Entrez votre mot de passe : ",
            validate=PasswordValidator(
                length=8,
                cap=True,
                number=True,
                message="Au moins 8 caractères, incluant une majuscule et un chiffre.",
            ),
        ).execute()

        # Appel du service pour créer l'utilisateur
        utilisateur = UtilisateurService().creer_compte(pseudo, mdp)

        # Si l'utilisateur a été créé
        if utilisateur:
            message = (
                f"Votre compte {utilisateur.pseudo} a été créé. "
                "Vous pouvez maintenant vous connecter."
            )
        else:
            message = "Erreur lors de la création du compte (pseudo ou mot de passe invalide)."

        from src.view.accueil.accueil_vue import AccueilVue

        return AccueilVue(message)
