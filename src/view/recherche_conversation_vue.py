import logging
from datetime import datetime

from InquirerPy import inquirer

from service.conversation_service import ConversationService, ErreurValidation
from view.session import Session
from view.vue_abstraite import VueAbstraite


class RechercheConversationVue(VueAbstraite):
    """Vue de recherche de conversations par mot-clé et/ou date."""

    def __init__(self, message: str = ""):
        self.message = message

    def choisir_menu(self):
        # 1) Sécurité : utilisateur connecté
        utilisateur = Session().utilisateur
        if utilisateur is None:
            from view.accueil.accueil_vue import AccueilVue

            print("hr")
            return AccueilVue("Veuillez vous connecter pour rechercher des conversations.")
        print("\n" + "-" * 50)
        print("Rechercher une conversation")
        print("-" * 50 + "\n")

        if self.message:
            print(self.message + "\n")
        print("hr")
        try:
            # 2) Saisie des critères (facultatifs)
            mot_cle = inquirer.text(
                message="Mot-clé (laisser vide si aucun) : ", default=""
            ).execute()

            date_str = inquirer.text(
                message="Date (YYYY-MM-DD, laisser vide si aucune) : ", default=""
            ).execute()

            # Normalisations
            mot_cle = mot_cle.strip() or None
            date_recherche = None

            # 3) Parsing de la date si fournie
            #    - si mot_cle ET date => DAO.rechercher_conv_motC_et_date attend un 'date'
            #    - si seulement date  => DAO.rechercher_date attend un 'datetime'
            if date_str.strip():
                try:
                    dt = datetime.strptime(date_str.strip(), "%Y-%m-%d")
                except ValueError:
                    return RechercheConversationVue("Format de date invalide. Utilisez YYYY-MM-DD.")

                if mot_cle:
                    date_recherche = dt.date()  # pour rechercher_conv_motC_et_date (type date)
                else:
                    date_recherche = dt  # pour rechercher_date (type datetime)

            # 4) Appel service
            resultats = ConversationService.rechercher_conversations(
                id_utilisateur=utilisateur.id,
                mot_cle=mot_cle,
                date_recherche=date_recherche,
            )

            # 5) Affichage des résultats
            if not resultats:
                print("\nAucune conversation ne correspond à vos critères.\n")
            else:
                print(f"\n{len(resultats)} conversation(s) trouvée(s) :\n")
                for conv in resultats:
                    # conv.date_creation peut être datetime/None : on gère gentiment
                    try:
                        d = conv.date_creation.strftime("%Y-%m-%d %H:%M")
                    except Exception:
                        d = str(conv.date_creation) if conv.date_creation is not None else "?"
                    print(f"- [{conv.id}] {conv.nom}  (créée le {d})")

                print("")

            # 6) Retour au menu utilisateur
            from view.menu_utilisateur_vue import MenuUtilisateurVue

            return MenuUtilisateurVue("Recherche terminée.")

        except ErreurValidation as e:
            # Erreurs métier (ex: prompt/date invalides côté service)
            return RechercheConversationVue(f"{e}")

        except Exception as e:
            logging.error(f"[RechercheConversationVue] Erreur inattendue : {e}")
            return RechercheConversationVue("Une erreur est survenue. Veuillez réessayer.")
