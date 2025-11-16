from collections import Counter
from typing import Iterable, List


class Statistiques:
    """
    Objet métier représentant des statistiques d'utilisation.

    Attributs
    -------------------------
    nb_conversations : int
        nombre total de conversations
    nb_messages : int
        nombre total de messages échangés
    heures_utilisation : float
        temps d'utilisation cumulé (en ?)
    sujets_plus_frequents : list[str]
        liste des sujets les plus fréquents (vue matérielle)

    Remarques d'implémentation
    --------------------------
    - On maintient un compteur interne (_sujet_counts) pour calculer
      efficacement les sujets les plus fréquents.
    - `sujets_plus_frequents` est exposé comme une liste, recalculée
      à partir du compteur lorsque nécessaire.
    """

    def __init__(
        self,
        nb_conversations: int = 0,
        nb_messages: int = 0,
        heures_utilisation: float = 0.0,
        sujets_plus_frequents: Iterable[str] | None = None,
    ):
        """
        Initialise un objet statistiques avec des valeurs éventuellement déjà existantes.

        Parameters
        ----------
        nb_conversations : int, optional
            Nombre initial de conversations.
        nb_messages : int, optional
            Nombre initial de messages.
        heures_utilisation : float, optional
            Temps initial d'utilisation.
        sujets_plus_frequents : Iterable[str] | None, optional
            Sujets initiaux à ajouter au compteur des sujets.
        """
        self.nb_conversations = int(nb_conversations)
        self.nb_messages = int(nb_messages)
        self.heures_utilisation = float(heures_utilisation)

        # Compteur interne pour les sujets
        self._sujet_counts: Counter[str] = Counter()
        if sujets_plus_frequents:
            self.ajouter_sujets(sujets_plus_frequents)

        # Vue matérielle
        self.sujets_plus_frequents: List[str] = self._rebuild_top_sujets()

    # --------- Méthodes métier / utilitaires ---------

    def incrementer_conversations(self, n: int = 1) -> None:
        """
        Incrémente le nombre total de conversations.

        Parameters
        ----------
        n : int, optional
            Nombre d'unités à ajouter (par défaut 1).
        """
        self.nb_conversations += int(n)

    def incrementer_messages(self, n: int = 1) -> None:
        """
        Incrémente le nombre total de messages.

        Parameters
        ----------
        n : int, optional
            Nombre d'unités à ajouter (par défaut 1).
        """
        self.nb_messages += int(n)

    def ajouter_temps(self, heures: float) -> None:
        """
        Ajoute un temps (en heures) au cumul d'utilisation.

        Parameters
        ----------
        heures : float
            Temps à ajouter.
        """
        self.heures_utilisation += float(heures)

    def ajouter_sujets(self, sujets: Iterable[str]) -> None:
        """
        Ajoute une collection de sujets dans le compteur interne et met à
        jour la liste des sujets les plus fréquents.

        Parameters
        ----------
        sujets : Iterable[str]
            Liste ou collection de sujets à ajouter (chaînes non vides).
        """
        self._sujet_counts.update(s.strip() for s in sujets if isinstance(s, str) and s.strip())
        self.sujets_plus_frequents = self._rebuild_top_sujets()

    def top_sujets(self, k: int = 10) -> List[str]:
        """
        Retourne les k sujets les plus fréquents.

        Ce calcul se fait à la volée à partir du compteur interne.

        Parameters
        ----------
        k : int, optional
            Nombre maximum de sujets à retourner.

        Returns
        -------
        List[str]
            Liste des k sujets les plus fréquents.
        """
        return [s for s, _ in self._sujet_counts.most_common(k)]

    def vider_sujets(self) -> None:
        """
        Réinitialise complètement la liste et le compteur des sujets.
        """
        self._sujet_counts.clear()
        self.sujets_plus_frequents = []

    def fusionner(self, autre: "Statistiques") -> "Statistiques":
        """
        Fusionne les statistiques d'un autre objet `Statistiques` dans celui-ci.

        Cette opération additionne les conversations, messages,
        heures d'utilisation et fusionne les compteurs de sujets.

        Parameters
        ----------
        autre : Statistiques
            Objet dont les valeurs doivent être fusionnées avec celles-ci.

        Returns
        -------
        Statistiques
            Le même objet courant, afin de permettre l'utilisation d'un
            pattern fluent (ex : `stats.fusionner(a).fusionner(b)`).
        """
        self.nb_conversations += autre.nb_conversations
        self.nb_messages += autre.nb_messages
        self.heures_utilisation += autre.heures_utilisation
        self._sujet_counts.update(autre._sujet_counts)
        self.sujets_plus_frequents = self._rebuild_top_sujets()
        return self

    # --------- Représentations ---------

    def afficher_stats(self) -> str:
        """
        Retourne une représentation textuelle lisible des statistiques.

        Returns
        -------
        str
            Chaîne concise contenant les valeurs principales et les cinq
            sujets les plus fréquents.
        """
        top5 = ", ".join(self.top_sujets(5)) or "—"
        return (
            "Statistiques("
            f"conversations={self.nb_conversations}, "
            f"messages={self.nb_messages}, "
            f"heures={self.heures_utilisation:.2f}, "
            f"top_sujets=[{top5}]"
            ")"
        )

    def __str__(self) -> str:
        """
        Représentation par défaut de l'objet, alias de `afficher_stats()`.

        Returns
        -------
        str
            Chaîne de représentation lisible.
        """
        return self.afficher_stats()

    # --------- Interne ---------

    def _rebuild_top_sujets(self, k: int = 10) -> List[str]:
        """
        Recalcule la liste des k sujets les plus fréquents à partir du
        compteur interne.

        Parameters
        ----------
        k : int, optional
            Nombre maximum de sujets à retourner.

        Returns
        -------
        List[str]
            Liste triée des sujets les plus fréquents.
        """
        return [s for s, _ in self._sujet_counts.most_common(k)]