import os
import pytest

from unittest.mock import patch

from src.utils.reset_database import ResetDatabase
from src.utils.securite import hash_password

from src.dao.conversation_dao import ConversationDAO

from src.business_object.conversation import Conversation


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
    #THEN
    assert isinstance(res, Conversation)
