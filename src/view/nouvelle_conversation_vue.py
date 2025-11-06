import logging

from InquirerPy import inquirer

from service.conversation_service import ConversationService, ErreurValidation
from view.session import Session
from view.vue_abstraite import VueAbstraite


class NouvelleConversationVue(VueAbstraite):
    """Vue de création d'une nouvelle conversation."""

    def __init__(self, message: str = ""):
        self.message = message

    def choisir_menu(self):
        # 1) Sécurité : utilisateur connecté
        utilisateur = Session().utilisateur
        if utilisateur is None:
            from view.accueil.accueil_vue import AccueilVue

            return AccueilVue("Veuillez vous connecter pour créer une conversation.")

        print("\n" + "-" * 50)
        print("Créer une nouvelle conversation")
        print("-" * 50 + "\n")

        if self.message:
            print(self.message + "\n")

        try:
            # 2) Saisie des champs
            titre = inquirer.text(
                message="Titre de la conversation : ",
                default="Nouvelle conversation",
            ).execute()

            # Personnalisation (profil / prompt système)
            # Tu peux mettre ici un select si tu as une liste de prompts en BDD
            personnalisation = inquirer.text(
                message="Nom du profil de personnalisation (ex: 'par_defaut') : ",
                default="",
            ).execute()

            # Normaliser : vide -> None
            if not personnalisation or not personnalisation.strip():
                personnalisation = None
            print(personnalisation)

            print("coucou")
            # 3) Appel service
            # ConversationService.creer_conv(...) doit lever ErreurValidation en cas d'inputs invalides
            msg = ConversationService.creer_conv(
                titre=titre,
                personnalisation=personnalisation,
                id_proprietaire=utilisateur.id,
            )

            print(msg)

            # 4) Succès → retour au menu utilisateur avec message
            from view.menu_utilisateur_vue import MenuUtilisateurVue

            return MenuUtilisateurVue(msg)

        except ErreurValidation as e:
            # Rester sur la même vue et afficher l'erreur “métier”
            return NouvelleConversationVue(f"{e}")

        except Exception as e:
            # Autres erreurs (DAO, SQL, etc.) → log + rester ici
            logging.error(f"[NouvelleConversationVue] Erreur inattendue: {e}")
            return NouvelleConversationVue("Une erreur est survenue. Veuillez réessayer.")
