import logging

from InquirerPy import inquirer

from src.dao.utilisateur_dao import UtilisateurDao
from src.service.auth_service import Auth_Service
from src.view.session import Session
from src.view.vue_abstraite import VueAbstraite


class MenuUtilisateurVue(VueAbstraite):
    """Vue principale du menu utilisateur (post-connexion)."""

    def __init__(self, message: str = ""):
        self.message = message

    def choisir_menu(self):
        """Affiche le menu utilisateur et gère la navigation."""
        logging.debug("Entrée dans MenuUtilisateurVue (message=%r)", self.message)

        # Vérifie que l'utilisateur est bien connecté
        utilisateur = Session().utilisateur
        if utilisateur is None:
            logging.warning(
                "[MenuUtilisateurVue] Accès sans utilisateur connecté, redirection vers AccueilVue."
            )
            from src.view.accueil.accueil_vue import AccueilVue

            return AccueilVue("Veuillez vous connecter avant d'accéder au menu utilisateur.")

        logging.debug(
            "Affichage du menu utilisateur pour user_id=%s, pseudo=%r",
            getattr(utilisateur, "id", None),
            getattr(utilisateur, "pseudo", None),
        )

        print("\n" + "-" * 50)
        print(f"Menu Utilisateur — {utilisateur.pseudo}")
        print("-" * 50 + "\n")

        if self.message:
            print(self.message + "\n")

        try:
            choix = inquirer.select(
                message="Faites votre choix : ",
                choices=[
                    "Voir mes conversations",
                    "Créer une nouvelle conversation",
                    "Rechercher une conversation",
                    "Voir mes statistiques",
                    "Infos de session",
                    "Se déconnecter",
                ],
            ).execute()

            logging.info(
                "[MenuUtilisateurVue] Choix utilisateur pour pseudo=%r : %r",
                utilisateur.pseudo,
                choix,
            )

            match choix:
                case "Se déconnecter":
                    logging.info(
                        "[MenuUtilisateurVue] Demande de déconnexion pour pseudo=%r",
                        utilisateur.pseudo,
                    )
                    s = Session()
                    token = s.token
                    if token:
                        logging.debug(
                            "[MenuUtilisateurVue] Invalidation du token pour pseudo=%r",
                            utilisateur.pseudo,
                        )
                        auth_service = Auth_Service(UtilisateurDao())
                        auth_service.se_deconnecter(token)
                    s.deconnexion()
                    from src.view.accueil.accueil_vue import AccueilVue

                    logging.info(
                        "[MenuUtilisateurVue] Déconnexion effectuée pour pseudo=%r",
                        utilisateur.pseudo,
                    )
                    return AccueilVue("Déconnexion effectuée avec succès.")

                case "Infos de session":
                    logging.debug(
                        "[MenuUtilisateurVue] Affichage des infos de session pour pseudo=%r",
                        utilisateur.pseudo,
                    )
                    return MenuUtilisateurVue(Session().afficher())

                case "Voir mes conversations":
                    from src.view.conversations_vue import ConversationsVue

                    logging.info(
                        "[MenuUtilisateurVue] Navigation vers ConversationsVue pour pseudo=%r",
                        utilisateur.pseudo,
                    )
                    return ConversationsVue()

                case "Créer une nouvelle conversation":
                    from src.view.nouvelle_conversation_vue import NouvelleConversationVue

                    logging.info(
                        "[MenuUtilisateurVue] Navigation vers NouvelleConversationVue pour pseudo=%r",
                        utilisateur.pseudo,
                    )
                    return NouvelleConversationVue()

                case "Rechercher une conversation":
                    from src.view.recherche_conversation_vue import RechercheConversationVue

                    logging.info(
                        "[MenuUtilisateurVue] Navigation vers RechercheConversationVue pour pseudo=%r",
                        utilisateur.pseudo,
                    )
                    return RechercheConversationVue()

                case "Voir mes statistiques":
                    from src.view.stats_vue import StatsVue

                    logging.info(
                        "[MenuUtilisateurVue] Navigation vers StatsVue pour pseudo=%r",
                        utilisateur.pseudo,
                    )
                    return StatsVue()

        except Exception as e:
            logging.error(f"[MenuUtilisateurVue] Erreur : {e}")
            # Revenir sur la même vue avec un message d’erreur
            return MenuUtilisateurVue("Une erreur est survenue, veuillez réessayer.")

        # Par défaut, si rien n’a été choisi
        logging.warning(
            "[MenuUtilisateurVue] Aucun choix valide retourné pour pseudo=%r, retour sur la même vue.",
            utilisateur.pseudo,
        )
        return MenuUtilisateurVue("Choix invalide ou annulé, veuillez réessayer.")
