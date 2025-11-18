import logging

import dotenv

from src.dao.utilisateur_dao import UtilisateurDao
from src.service.auth_service import Auth_Service

# Ajouts pour la déconnexion si l'utilisateur fait un ctrl+c
from src.view.session import Session
from utils.log_init import initialiser_logs
from view.accueil.accueil_vue import AccueilVue

if __name__ == "__main__":
    # On charge les variables d'envionnement
    dotenv.load_dotenv(override=True)

    initialiser_logs("Application")

    vue_courante = AccueilVue("Bienvenue")
    nb_erreurs = 0

    try:
        while vue_courante:
            if nb_erreurs > 100:
                print("Le programme recense trop d'erreurs et va s'arrêter")
                break
            try:
                # Affichage du menu
                vue_courante.afficher()

                # Affichage des choix possibles
                vue_courante = vue_courante.choisir_menu()

            except Exception as e:
                logging.info(e)
                nb_erreurs += 1
                vue_courante = AccueilVue("Une erreur est survenue, retour au menu principal")

    except KeyboardInterrupt:
        # Gestion du Ctrl + C (arrêt propre)
        print("\n\nInterruption détectée (Ctrl + C).")
        print("Fermeture propre de la session...")

        s = Session()
        if s.utilisateur:
            # Invalidation du token si nécessaire
            if s.token:
                try:
                    auth_service = Auth_Service(UtilisateurDao())
                    auth_service.se_deconnecter(s.token)
                except Exception:
                    pass  # on n'arrête pas pour ça

            # Fermeture de la session BDD + reset
            try:
                s.deconnexion()
            except Exception:
                pass

            print("Session correctement terminée.")
        else:
            print("Aucune session ouverte.")

    # Lorsque l on quitte l application (cas normal ou Ctrl+C)
    print("----------------------------------")
    print("Au revoir")

    logging.info("Fin de l'application")
