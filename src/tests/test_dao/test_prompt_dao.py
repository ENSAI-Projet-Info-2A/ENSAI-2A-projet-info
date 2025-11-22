import os
from unittest.mock import patch

import pytest

from src.dao.prompt_dao import PromptDAO
from src.utils.reset_database import ResetDatabase


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialisation des données de test pour les DAO de prompts."""
    with patch.dict(os.environ, {"SCHEMA": "projet_test_dao"}):
        ResetDatabase().lancer(test_dao=True)
        yield


def test_obtenir_id_par_nom_existant():
    """
    Vérifie que obtenir_id_par_nom renvoie bien un id pour un nom connu.

    Les noms existants sont insérés dans data/pop_db_test.sql :
    - fr_tuteur_strict_v2
    - math_tuteur
    - codeur_python
    - math_prof
    """
    prompt_id = PromptDAO.obtenir_id_par_nom("fr_tuteur_strict_v2")
    assert isinstance(prompt_id, int)
    assert prompt_id > 0


def test_obtenir_id_par_nom_inexistant():
    """obtenir_id_par_nom doit renvoyer None si le nom de prompt n'existe pas."""
    prompt_id = PromptDAO.obtenir_id_par_nom("nom_qui_n_existe_pas_du_tout")
    assert prompt_id is None


def test_existe_id_true_false():
    """Teste existe_id avec un id valide puis un id invalide."""
    # On récupère d'abord un id valide
    prompt_id = PromptDAO.obtenir_id_par_nom("math_tuteur")
    assert prompt_id is not None

    assert PromptDAO.existe_id(prompt_id) is True
    assert PromptDAO.existe_id(999999) is False


def test_lister_prompts_retourne_liste_non_vide():
    """lister_prompts doit renvoyer une liste de dict avec au moins 1 élément."""
    prompts = PromptDAO.lister_prompts()

    assert isinstance(prompts, list)
    assert len(prompts) >= 1

    first = prompts[0]
    assert "id" in first
    assert "nom" in first
    assert isinstance(first["id"], int)
    assert isinstance(first["nom"], str)


def test_obtenir_texte_prompt_par_id_existant():
    """obtenir_texte_prompt_par_id renvoie bien le texte pour un id existant."""
    prompts = PromptDAO.lister_prompts()
    prompt_id = prompts[0]["id"]

    texte = PromptDAO.obtenir_texte_prompt_par_id(prompt_id)

    assert isinstance(texte, str)
    assert len(texte) > 0


def test_obtenir_texte_prompt_par_id_inexistant():
    """obtenir_texte_prompt_par_id renvoie None pour un id inexistant."""
    texte = PromptDAO.obtenir_texte_prompt_par_id(987654321)
    assert texte is None
