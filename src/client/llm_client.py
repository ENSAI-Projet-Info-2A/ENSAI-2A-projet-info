from typing import List, Optional

from business_object.echange import Echange


class LLM_API:
    """
    Client pour l'API LLM (Large Language Model).
    Permet de générer une réponse en envoyant l'historique de la conversation.
    """

    def generate(
        self,
        history: List[Echange],
        temperature: float,
        top_p: float,
        max_tokens: int,
        stop: Optional[List[str]] = None,
    ) -> Echange:
        """
        Envoie l'historique au modèle et retourne un nouvel échange (réponse de l'assistant).

        Parameters
        ----------
        history : List[Echange]
            Historique de la conversation (messages précédents).
        temperature : float
            Contrôle la créativité de la génération.
        top_p : float
            Paramètre nucleus sampling (1.0 = pas de filtrage).
        max_tokens : int
            Nombre maximum de tokens générés.
        stop : Optional[List[str]]
            Séquences d’arrêt éventuelles.

        Returns
        -------
        Echange
            Réponse générée par le modèle.
        """
        pass
