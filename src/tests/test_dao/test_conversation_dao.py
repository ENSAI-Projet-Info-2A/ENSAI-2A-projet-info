import os
from unittest.mock import patch

import pytest

from src.business_object.conversation import Conversation
from src.dao.conversation_dao import ConversationDAO
from src.utils.reset_database import ResetDatabase
from datetime import datetime


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialisation des données de test"""
    with patch.dict(os.environ, {"SCHEMA": "projet_test_dao"}):
        ResetDatabase().lancer(test_dao=True)
        yield


def test_creer_conversation_valide():
    # GIVEN
    conv = Conversation(id=100, nom="conv_test")
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
    conv = Conversation(id=300, nom="ancien_nom")
    conv = ConversationDAO.creer_conversation(conv)
    id_conv = conv.id
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
    id_conv = "mauvais_id"
    nouveau_nom = "nouveau_nom_test_fail"
    # WHEN + THEN
    with pytest.raises(Exception) as exc_info:
        ConversationDAO.renommer_conv(id_conv, nouveau_nom)
    assert "l'id mauvais_id est invalide et doit être un entier naturel" in str(exc_info.value)


def test_supprimer_conv():
    # GIVEN
    conv = Conversation(nom="conv_test_a_supprimer")
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
    assert isinstance(res[0].id, int)
    assert res[0].id == 3
    assert res[1].id == 1


# 9 dans conv 1 et 3
def test_retirer_participant_ok():
    # WHEN
    res = TaClasse.retirer_participant(conversation_id=5, id_user=9)

    # THEN
    assert res is True

def test_ajouter_echange_ia():
    #GIVEN
    id_conv=32
    e = Echange(id="18", agent="ia", message="Hello", date_msg='2025-05-09 14:56:33+00')

    # WHEN
    res = ConversationDAO.ajouter_echange(id_conv, e)

    # THEN
    assert res is True
    assert isinstance(e.id, int)
    assert e.id == 42

def test_agent_invalide():
    # GIVEN
    e = Echange(id="18", agent="robot", message="Hello", date_msg='2025-05-09 14:56:33+00')

    # WHEN / THEN
    with pytest.raises(Exception):
        ConversationDAO.ajouter_echange(1, e)


def test_compter_message_user():
    #GIVEN la bdd pour les tests
     # WHEN
    result = ConversationDAO.compter_message_user(9)

     # THEN
    assert isinstance(result, int)
    assert result == 1 # 1 messages "utilisateur" pour id_user=9

def test_compter_message_user_aucun():

    # WHEN
    result = ConversationDAO.compter_message_user(999) # id_user inexistant

    # THEN
    assert isinstance(result, int)
    assert result == 0

def test_sujets_plus_frequents_ok():
    """Renvoie les k mots les plus fréquents d'un utilisateur"""
    # WHEN
    res = ConversationDAO.sujets_plus_frequents(id_user=9, k=3)

    # THEN
    assert isinstance(res, list)
    assert len(res) <= 3
    # ajouter à la bdd test des choses peremettants ca. mots = [mot for mot, _ in res]
    #assert "" in mots

def test_sujets_plus_frequents_aucune_conversation(mock_db): #okjepense
    """Lève une exception si l'utilisateur n'a aucune conversation"""
    # GIVEN
    id_user = 9999
    # WHEN / THEN
    with pytest.raises(Exception) as exc_info:
        ConversationDAO.sujets_plus_frequents(id_user, k=5)
    assert "aucune conversation" in str(exc_info.value).lower()
 #besoin d'un test limite ? titre vide ? etc ? 

