import logging

from InquirerPy import inquirer

from src.utils.reset_database import ResetDatabase
from src.view.accueil.connexion_vue import ConnexionVue
from src.view.accueil.inscription_vue import InscriptionVue
from src.view.session import Session
from src.view.vue_abstraite import VueAbstraite


class AccueilVue(VueAbstraite):
    """Vue d'accueil de l'application"""

    def __init__(self, message: str = ""):
        self.message = message

    def choisir_menu(self):
        """Retourne la vue choisie par l'utilisateur."""
        logging.debug("Affichage du menu d'accueil (message=%r)", self.message)

        print("\n" + "-" * 50 + "\nAccueil\n" + "-" * 50 + "\n")
        if self.message:
            print(self.message + "\n")

        choix = inquirer.select(
            message="Faites votre choix : ",
            choices=[
                "Se connecter",
                "Créer un compte",
                "Ré-initialiser la base de données",
                "Infos de session",
                "Quitter",
            ],
        ).execute()

        logging.info("Choix utilisateur dans AccueilVue : %r", choix)

        match choix:
            case "Quitter":
                logging.info("L'utilisateur a choisi de quitter l'application depuis l'accueil.")
                return None

            case "Se connecter":
                try:
                    logging.info("Navigation vers ConnexionVue.")
                    return ConnexionVue("Connexion à l'application")
                except Exception as e:
                    import traceback

                    logging.error(
                        "Erreur lors de l'ouverture de ConnexionVue : %s", e, exc_info=True
                    )
                    traceback.print_exc()
                    return AccueilVue(f"Échec d'ouverture de la page de connexion : {e}")

            case "Créer un compte":
                logging.info("Navigation vers InscriptionVue.")
                return InscriptionVue("Création de compte")

            case "Infos de session":
                logging.debug("Affichage des infos de session.")
                return AccueilVue(Session().afficher())

            case "Ré-initialiser la base de données":
                logging.warning("Demande de ré-initialisation de la base de données.")
                succes = ResetDatabase().lancer()
                message = (
                    f"Ré-initialisation de la base de données - {'SUCCÈS' if succes else 'ÉCHEC'}"
                )
                logging.info("Ré-initialisation BDD terminée : %s", message)
                return AccueilVue(message)
