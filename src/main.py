import logging

import dotenv

from src.dao.utilisateur_dao import UtilisateurDao
from src.service.auth_service import Auth_Service

# Ajouts pour la déconnexion si l'utilisateur fait un ctrl+c
from src.view.session import Session
from utils.log_init import initialiser_logs
from view.accueil.accueil_vue import AccueilVue

if __name__ == "__main__":
    # On charge les variables d'environnement
    dotenv.load_dotenv(override=True)
    initialiser_logs("Application")

    logging.info("Démarrage de l'application")

    vue_courante = AccueilVue("Bienvenue")
    nb_erreurs = 0

    try:
        while vue_courante:
            if nb_erreurs > 100:
                message = "Le programme recense trop d'erreurs et va s'arrêter"
                print(message)
                logging.error("Arrêt de l'application après %s erreurs consécutives", nb_erreurs)
                break
            try:
                # Affichage du menu
                logging.debug("Affichage de la vue %s", type(vue_courante).__name__)
                vue_courante.afficher()

                # Affichage des choix possibles
                vue_courante = vue_courante.choisir_menu()
                logging.debug(
                    "Vue suivante : %s",
                    type(vue_courante).__name__ if vue_courante else None,
                )

            except Exception:
                nb_erreurs += 1
                logging.exception(
                    "Erreur non gérée dans la boucle principale (nb_erreurs=%s)",
                    nb_erreurs,
                )
                vue_courante = AccueilVue("Une erreur est survenue, retour au menu principal")

    except KeyboardInterrupt:
        # Gestion du Ctrl + C (arrêt propre)
        print("\n\nInterruption détectée (Ctrl + C).")
        print("Fermeture propre de la session...")
        logging.warning("Interruption utilisateur (Ctrl + C), fermeture propre...")

        s = Session()
        if s.utilisateur:
            # Invalidation du token si nécessaire
            if s.token:
                try:
                    auth_service = Auth_Service(UtilisateurDao())
                    auth_service.se_deconnecter(s.token)
                    logging.info("Token utilisateur invalidé lors de la fermeture de session.")
                except Exception:
                    logging.exception("Échec lors de l'invalidation du token à la fermeture.")

            # Fermeture de la session BDD + reset
            try:
                s.deconnexion()
                logging.info("Session utilisateur déconnectée proprement.")
            except Exception:
                logging.exception("Erreur lors de la déconnexion de la session.")

            print("Session correctement terminée.")
        else:
            print("Aucune session ouverte.")
            logging.info("Ctrl + C sans session utilisateur active.")

    # Lorsque l'on quitte l'application (cas normal ou Ctrl+C)
    print("----------------------------------")
    print("Au revoir")

    logging.info("Fin de l'application")
