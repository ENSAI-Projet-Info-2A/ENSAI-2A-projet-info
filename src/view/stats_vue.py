import logging

from InquirerPy import inquirer

from src.service.stats_service import Statistiques_Service
from src.view.session import Session
from src.view.vue_abstraite import VueAbstraite


class StatsVue(VueAbstraite):
    """Tableau de bord utilisateur.

    Affiche des statistiques personnalisées :
      - nombre de conversations
      - nombre de messages envoyés
      - temps total d'utilisation
      - sujets de conversation les plus fréquents
    """

    def __init__(self, message: str = ""):
        self.message = message

    def choisir_menu(self):
        # 1) Vérifier qu'un utilisateur est connecté
        session = Session()
        utilisateur = session.utilisateur
        if utilisateur is None:
            from src.view.accueil.accueil_vue import AccueilVue

            return AccueilVue("Veuillez vous connecter pour accéder à votre tableau de bord.")

        # 2) Récupérer les statistiques via le service
        try:
            service = Statistiques_Service()
            stats = service.stats_utilisateur(utilisateur.id)
        except Exception as exc:
            logging.error(f"[StatsVue] Erreur lors du calcul des statistiques : {exc}")
            from src.view.menu_utilisateur_vue import MenuUtilisateurVue

            return MenuUtilisateurVue("Une erreur est survenue lors du calcul des statistiques.")

        # 3) Affichage du tableau de bord
        print("\n" + "-" * 50)
        print(f"Tableau de bord — {utilisateur.pseudo}")
        print("-" * 50 + "\n")

        if self.message:
            print(self.message + "\n")

        # Bloc "chiffres clés"
        print("Vos chiffres clés :")
        print(f" • Conversations : {stats.nb_conversations}")
        print(f" • Messages envoyés : {stats.nb_messages}")

        # Temps total d'utilisation
        # Temps total d'utilisation (heures -> h/min/s)
        heures = float(getattr(stats, "heures_utilisation", 0.0) or 0.0)
        total_seconds = int(round(heures * 3600))

        if total_seconds <= 0:
            temps_str = "moins d'une seconde"
        else:
            h = total_seconds // 3600
            m = (total_seconds % 3600) // 60
            s = total_seconds % 60
            # Format compact HHh MMmin SSs
            temps_str = f"{h:02d}h {m:02d}min {s:02d}s"

        print(f" • Temps d'utilisation total : {temps_str}")

        # Indicateur dérivé : moyenne de messages par conversation
        if stats.nb_conversations > 0:
            moyenne = stats.nb_messages / stats.nb_conversations
            print(f" • Messages par conversation (moyenne) : {moyenne:.1f}")
        else:
            print(" • Messages par conversation (moyenne) : —")

        print()

        # 4) Sujets les plus fréquents
        top_sujets = []
        try:
            # On essaie d'utiliser la méthode dédiée si elle existe
            if hasattr(stats, "top_sujets"):
                top_sujets = stats.top_sujets(5)
            else:
                top_sujets = list(getattr(stats, "sujets_plus_frequents", []))[:5]
        except Exception as exc:  # pragma: no cover - robustesse
            logging.error(f"[StatsVue] Erreur lors de la récupération des sujets : {exc}")
            top_sujets = []

        print("Sujets les plus fréquents :")
        if top_sujets:
            for idx, sujet in enumerate(top_sujets, start=1):
                print(f"   {idx}. {sujet}")
        else:
            print("   Aucun sujet détecté pour le moment.")
        print()

        # 5) Menu suivant
        try:
            choix = inquirer.select(
                message="Que souhaitez-vous faire ?",
                choices=[
                    "↩︎ Retour au menu utilisateur",
                    "Actualiser les statistiques",
                ],
            ).execute()
        except Exception as exc:
            logging.error(f"[StatsVue] Erreur interaction Inquirer : {exc}")
            from src.view.menu_utilisateur_vue import MenuUtilisateurVue

            return MenuUtilisateurVue(
                "Une erreur est survenue lors de l'affichage du tableau de bord."
            )

        from src.view.menu_utilisateur_vue import MenuUtilisateurVue

        if choix == "↩︎ Retour au menu utilisateur":
            return MenuUtilisateurVue()

        # Par défaut : on recharge la vue pour rafraîchir les stats
        return StatsVue()
