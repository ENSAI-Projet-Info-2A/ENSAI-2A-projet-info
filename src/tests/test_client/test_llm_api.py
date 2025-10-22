# src/tests/test_client/test_llm_api.py
import json
import types
from unittest.mock import MagicMock

import pytest

from business_object.echange import Echange
from client.llm_client import LLM_API


def _fake_response_ok_type_mistral(text):
    """Construit un faux objet 'requests.Response' au format Mistral."""
    resp = types.SimpleNamespace()
    resp.ok = True
    resp.status_code = 200
    param = {
        "id": "abc123",
        "object": "chat.completion",
        "created": 1761121563,
        "model": "mistralai/Mistral-7B-Instruct-v0.3",
        "choices": [
            {
                "index": 0,
                "logprobs": None,
                "finish_reason": "stop",
                "message": {"role": "assistant", "content": text, "tool_calls": []},
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    }

    def _json():
        return param

    resp.json = _json
    resp.text = json.dumps(param)
    return resp


def _fake_response_http_error(status_code=422, detail="Validation Error"):
    """Fausse réponse HTTP avec code != 200 et détail JSON."""
    resp = types.SimpleNamespace()
    resp.ok = False
    resp.status_code = status_code

    def _json():
        return {"detail": detail}

    resp.json = _json
    resp.text = json.dumps({"detail": detail})
    return resp


def _fake_response_plain_text(txt="plain-text-response"):
    """Réponse où .json() lève ValueError et .text contient la réponse."""
    resp = types.SimpleNamespace()
    resp.ok = True
    resp.status_code = 200

    def _json():
        raise ValueError("Not a JSON")

    resp.json = _json
    resp.text = txt
    return resp


def test_generate_ok_openai_format(monkeypatch):
    """Succès : extraction de choices[0].message.content"""

    # GIVEN
    # on force l'URL pour éviter toute dépendance d'environnement
    monkeypatch.setenv("ENSAI_GPT_BASE_URL", "https://exemple.test")

    # Mock de requests.post -> renvoie une réponse OK type OpenAI
    import requests

    requests.post = MagicMock(return_value=_fake_response_ok_type_mistral("Bonjour"))

    api = LLM_API()
    history = [
        Echange(agent="system", message="Tu es un assistant utile."),
        Echange(agent="utilisateur", message="Dis bonjour"),
    ]

    # WHEN
    res = api.generate(history=history, temperature=0.7, top_p=1.0, max_tokens=32)

    # THEN
    assert isinstance(res, Echange)
    assert res.agent == "assistant"
    assert res.message == "Bonjour"

    # On vérifie aussi que l'appel a bien été fait avec le bon endpoint et un JSON structuré
    requests.post.assert_called_once()
    args, kwargs = requests.post.call_args
    assert args[0] == "https://exemple.test/generate"
    assert "json" in kwargs
    sent = kwargs["json"]
    # l'historique doit avoir deux messages mappés correctement
    assert sent["history"][0]["role"] == "system"
    assert sent["history"][1]["role"] == "user"  # 'utilisateur' -> 'user'
    assert sent["history"][1]["content"] == "Dis bonjour"
    assert sent["temperature"] == pytest.approx(0.7)
    assert sent["top_p"] == pytest.approx(1.0)
    assert sent["max_tokens"] == 32


def test_generate_http_error_returns_echange(monkeypatch):
    """Erreur HTTP : on renvoie un Echange 'assistant' avec le message d'erreur lisible."""
    # GIVEN
    monkeypatch.setenv("ENSAI_GPT_BASE_URL", "https://exemple.test")

    import requests

    requests.post = MagicMock(return_value=_fake_response_http_error(422, "Validation Error"))

    api = LLM_API()
    history = [Echange(agent="user", message="test")]

    # WHEN
    res = api.generate(history=history, temperature=0.1, top_p=1.0, max_tokens=10)

    # THEN
    assert isinstance(res, Echange)
    assert res.agent == "assistant"
    assert "Erreur 422" in res.message
    assert "Validation Error" in res.message


def test_generate_plain_text_response(monkeypatch):
    """Réponse texte brut : on renvoie le .text tel quel."""
    # GIVEN
    monkeypatch.setenv("ENSAI_GPT_BASE_URL", "https://exemple.test")

    import requests

    requests.post = MagicMock(return_value=_fake_response_plain_text("OK TEXTE BRUT"))

    api = LLM_API()
    history = [Echange(agent="user", message="test")]

    # WHEN
    res = api.generate(history=history, temperature=0, top_p=1, max_tokens=5)

    # THEN
    assert isinstance(res, Echange)
    assert res.message == "OK TEXTE BRUT"
