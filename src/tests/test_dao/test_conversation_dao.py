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
    assert isinstance(res, Conversation) 

