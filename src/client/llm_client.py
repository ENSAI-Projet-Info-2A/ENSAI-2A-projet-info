import json
import logging
import os
from typing import List, Optional

import requests

from src.business_object.echange import Echange


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
        Envoie l'historique de conversation à l'API et renvoie la réponse du modèle.
        """
        # URL du service
        base_url = os.getenv(
            "ENSAI_GPT_BASE_URL", "https://ensai-gpt-109912438483.europe-west4.run.app"
        )
        endpoint = base_url.rstrip("/") + "/generate"

        logging.debug(f"[LLM_API] generate() endpoint={endpoint}")

        def map_agent_to_role(agent: str) -> str:
            """Convertit l’attribut métier agent de Echange vers les rôles attendus par l’API si besoin"""
            if not agent:
                return "user"
            a = agent.lower()
            if a in {"system", "user", "assistant", "tool"}:
                return a
            # Mappages francisés ou synonymes
            if a in {"utilisateur"}:
                return "user"
            if a in {"assistant", "machine", "bot", "modele", "modèle", "ia"}:
                return "assistant"
            return "user"

        parameters = {
            "history": [
                {"role": map_agent_to_role(e.agent), "content": e.message} for e in history
            ],
            "temperature": max(0.0, min(2.0, float(temperature))),
            "top_p": max(0.0, min(1.0, float(top_p))),
            "max_tokens": int(max_tokens),
        }
        if stop:
            parameters["stop"] = list(stop)

        logging.debug(f"[LLM_API] payload envoyé : {parameters}")

        try:
            resp = requests.post(endpoint, json=parameters, timeout=30)
        except requests.RequestException as exc:
            logging.exception("Erreur de connexion à l'API LLM: %s", exc)
            return Echange(
                agent="assistant",
                agent_name="Assistant",
                message=f"Impossible de contacter le service LLM: {exc}",
            )

        if not resp.ok:
            logging.error(f"[LLM_API] Réponse HTTP {resp.status_code} : {resp.text[:200]}")
            try:
                j = resp.json()
                err_txt = j.get("detail") if isinstance(j, dict) else str(j)
            except Exception:
                err_txt = resp.text
            return Echange(
                agent="assistant",
                agent_name="Assistant",
                message=f"Erreur {resp.status_code} du service LLM: {err_txt}",
            )

        try:
            data = resp.json()
            logging.debug(f"[LLM_API] Réponse JSON brute reçue : {data}")
        except ValueError:
            data = resp.text
            logging.debug(f"[LLM_API] Réponse texte brute reçue : {data}")

        def extract_content(data):
            """Récupère le texte utile depuis les différents formats possibles de réponse."""
            # 1. Chaîne directe
            if isinstance(data, str):
                return data

            # 2. Format type Mistral
            if isinstance(data, dict):
                if "choices" in data and isinstance(data["choices"], list) and data["choices"]:
                    choice0 = data["choices"][0]
                    msg = choice0.get("message")
                    if isinstance(msg, dict):
                        if "content" in msg and msg["content"] is not None:
                            return str(msg["content"])
                        return str(msg)
                    if "text" in choice0 and choice0["text"] is not None:
                        return str(choice0["text"])

                # Autres formats possibles
                for key in ("content", "text", "message"):
                    if key in data and data[key] is not None:
                        return str(data[key])

                try:
                    return json.dumps(data, ensure_ascii=False)
                except Exception:
                    return str(data)

            return str(data)

        content = extract_content(data)

        logging.info("[LLM_API] Réponse extraite avec succès depuis l'API")

        return Echange(agent="assistant", agent_name="Assistant", message=content)
