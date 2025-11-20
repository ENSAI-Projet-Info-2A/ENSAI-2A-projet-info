import logging

from InquirerPy import inquirer

from src.service.conversation_service import ConversationService, ErreurValidation
from src.view.session import Session
from src.view.vue_abstraite import VueAbstraite


class NouvelleConversationVue(VueAbstraite):
    """Vue de création d'une nouvelle conversation."""

    def __init__(self, message: str = ""):
        self.message = message

    def choisir_menu(self):
        logging.debug("Entrée dans NouvelleConversationVue (message=%r)", self.message)

        # 1) Sécurité : utilisateur connecté
        utilisateur = Session().utilisateur
        if utilisateur is None:
            logging.warning(
                "[NouvelleConversationVue] Accès sans utilisateur connecté, redirection AccueilVue."
            )
            from src.view.accueil.accueil_vue import AccueilVue

            return AccueilVue("Veuillez vous connecter pour créer une conversation.")

        logging.debug(
            "[NouvelleConversationVue] Création de conversation demandée par user_id=%s, pseudo=%r",
            getattr(utilisateur, "id", None),
            getattr(utilisateur, "pseudo", None),
        )

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
            logging.info(
                "[NouvelleConversationVue] Titre saisi pour nouvelle conversation : %r",
                titre,
            )

            # Personnalisation (profil / prompt système)
            # Tu peux mettre ici un select si tu as une liste de prompts en BDD
            personnalisation = inquirer.text(
                message="Nom du profil de personnalisation (ex: 'par_defaut') : ",
                default="",
            ).execute()

            logging.debug(
                "[NouvelleConversationVue] Personnalisation saisie (brut) : %r",
                personnalisation,
            )

            # Normaliser : vide -> None
            if not personnalisation or not personnalisation.strip():
                personnalisation = None

            logging.debug(
                "[NouvelleConversationVue] Personnalisation normalisée : %r",
                personnalisation,
            )

            # 3) Appel service
            # ConversationService.creer_conv(...) doit lever ErreurValidation en cas d'inputs invalides
            logging.info(
                "[NouvelleConversationVue] Appel ConversationService.creer_conv(titre=%r, perso=%r, proprietaire_id=%s)",
                titre,
                personnalisation,
                utilisateur.id,
            )
            msg = ConversationService.creer_conv(
                titre=titre,
                personnalisation=personnalisation,
                id_proprietaire=utilisateur.id,
            )
            logging.info(
                "[NouvelleConversationVue] Conversation créée avec succès pour user_id=%s : %s",
                utilisateur.id,
                msg,
            )

            # 4) Succès → retour au menu utilisateur avec message
            from src.view.menu_utilisateur_vue import MenuUtilisateurVue

            return MenuUtilisateurVue(msg)

        except ErreurValidation as e:
            # Rester sur la même vue et afficher l'erreur “métier”
            logging.warning(
                "[NouvelleConversationVue] Erreur de validation lors de la création de conversation : %s",
                e,
            )
            return NouvelleConversationVue(f"{e}")

        except Exception as e:
            # Autres erreurs (DAO, SQL, etc.) → log + rester ici
            logging.error(f"[NouvelleConversationVue] Erreur inattendue: {e}")
            return NouvelleConversationVue("Une erreur est survenue. Veuillez réessayer.")
