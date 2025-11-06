import os
import pytest

from unittest.mock import patch

from utils.reset_database import ResetDatabase
from utils.securite import hash_password

from dao.conversation_dao import ConversationDAO

from business_object.conversation import Conversation


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialisation des données de test"""
    with patch.dict(os.environ, {"SCHEMA": "projet_test_dao"}):
        ResetDatabase().lancer(test_dao=True)
        yield


def test_creer_conversation_valide():
    # GIVEN 
    conv = Conversation(id = 100, nom= "conv_test")
    print(conv)
    # WHEN
    res = ConversationDAO.creer_conversation(conv)
    # THEN
    assert isinstance(res, Conversation)

def test_trouver_par_id():
    # GIVEN
    id_conv = 3
    # WHEN 
    res = ConversationDAO.trouver_par_id(id_conv=id_conv)
    # THEN 
    assert id_conv == res.id

def test_trouver_par_id_fail():
    # GIVEN 
    id_inexistant = 333333333333
    # WHEN + THEN 
    with pytest.raises(Exception) as exc_info:
        ConversationDAO.trouver_par_id(id_conv=id_inexistant)
    assert "Aucune conversation trouvée avec id=333333333333" in str(exc_info.value)

def test_renommer_conv():
    # GIVEN
    id_conv = 4
    nouveau_nom = "nouveau_nom_test"
    # WHEN 
    res = ConversationDAO.renommer_conv(id_conv, nouveau_nom)
    # THEN 
    assert res == "titre modifié avec succès" 

def test_renommer_conv_fail_1():
    # GIVEN
    id_conv = 333333333333
    nouveau_nom = "nouveau_nom_test_fail"
    # WHEN + THEN 
    with pytest.raises(Exception) as exc_info:
        ConversationDAO.renommer_conv(id_conv, nouveau_nom)
    assert "Erreur dans la modification du titre pour id_conv = 333333333333" in str(exc_info.value)

def test_renommer_conv_fail_2():
    # GIVEN
    id_conv = 'mauvais_id'
    nouveau_nom = "nouveau_nom_test_fail"
    # WHEN + THEN 
    with pytest.raises(Exception) as exc_info:
        ConversationDAO.renommer_conv(id_conv, nouveau_nom)
    assert "l'id mauvais_id est invalide et doit être un entier naturel" in str(exc_info.value)

def test_supprimer_conv():
    # GIVEN
    conv = Conversation(nom= "conv_test_a_supprimer")
    conv_a_sup = ConversationDAO.creer_conversation(conv)
    id_conv_a_sup = conv_a_sup.id
    # WHEN
    res = ConversationDAO.supprimer_conv(id_conv_a_sup)
    # THEN 
    assert res == f"la conversation d'id={id_conv_a_sup} a bien été supprimée"

def test_supprimer_conv_fail():
    # GIVEN 
    id_conv = 200000
    # WHEN + THEN 
    with pytest.raises(Exception) as exc_info:
        ConversationDAO.supprimer_conv(id_conv)
    assert "echec de la suppression de la conversation d'identifiant 20000" in str(exc_info.value)

def test_supprimer_conv_fail_2():
    # GIVEN 
    id_conv = "mauvais_id"
    # WHEN + THEN 
    with pytest.raises(Exception) as exc_info:
        ConversationDAO.supprimer_conv(id_conv)
    assert "l'id mauvais_id est invalide et doit être un entier naturel" in str(exc_info.value)

def test_lister_conv():
    # GIVEN 
    id_user = 9
    # WHEN 
    res = ConversationDAO.lister_conversations(id_user)

    # THEN 
    assert type(res[0].id) == int
    assert res[0].id == 1
# 9 dans conv 1 et 3



