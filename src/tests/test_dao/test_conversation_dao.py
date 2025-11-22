import datetime
import os
from unittest.mock import patch

import pytest

from src.business_object.conversation import Conversation
from src.business_object.echange import Echange
from src.dao.conversation_dao import ConversationDAO
from src.dao.prompt_dao import PromptDAO
from src.utils.reset_database import ResetDatabase


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
    res = ConversationDAO.retirer_participant(conversation_id=3, id_user=9)

    # THEN
    assert res is True


def test_ajouter_echange_ia():
    # GIVEN : créer une conversation réelle
    conv = Conversation(nom="conv_test_echange")
    conv = ConversationDAO.creer_conversation(conv)
    id_conv = conv.id

    e = Echange(
        id=None,  # on laisse la BDD gérer
        agent="ia",
        message="Hello",
        date_msg="2025-05-09 14:56:33+00",
    )

    # WHEN
    res = ConversationDAO.ajouter_echange(id_conv, e)

    # THEN
    assert res is True
    assert isinstance(e.id, int)
    assert e.id > 0


def test_agent_invalide():
    # GIVEN
    e = Echange(id="18", agent="robot", message="Hello", date_msg="2025-05-09 14:56:33+00")

    # WHEN / THEN
    with pytest.raises(Exception):
        ConversationDAO.ajouter_echange(1, e)


def test_compter_message_user():
    # GIVEN la bdd pour les tests
    # WHEN
    result = ConversationDAO.compter_message_user(9)

    # THEN
    assert isinstance(result, int)
    assert result == 1  # 1 messages "utilisateur" pour id_user=9


def test_compter_message_user_aucun():
    # WHEN
    result = ConversationDAO.compter_message_user(999)  # id_user inexistant

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
    # assert "" in mots


def test_sujets_plus_frequents_aucune_conversation():
    """Lève une exception si l'utilisateur n'a aucune conversation"""
    # GIVEN
    id_user = 9999
    # WHEN / THEN
    with pytest.raises(Exception) as exc_info:
        ConversationDAO.sujets_plus_frequents(id_user, k=5)
    assert "aucune conversation" in str(exc_info.value).lower()


def test_creer_conversation_titre_vide():
    """Titre vide → ValueError dans creer_conversation."""
    conv = Conversation(nom="")
    with pytest.raises(ValueError):
        ConversationDAO.creer_conversation(conv)


def test_creer_conversation_prompt_nom_valide():
    """
    personnalisation = str correspondant à un prompt existant en base
    → la conversation est créée avec le bon prompt_id.
    """
    # 'fr_tuteur_strict_v2' existe dans pop_db_test.sql avec id = 1
    conv = Conversation(nom="Conv avec prompt", personnalisation="fr_tuteur_strict_v2")

    conv = ConversationDAO.creer_conversation(conv, proprietaire_id=5)

    # On vérifie que le prompt_id a bien été résolu et stocké
    assert conv.personnalisation == 1  # id du prompt 'fr_tuteur_strict_v2'
    # Et que le propriétaire est bien enregistré comme participant
    assert ConversationDAO.est_proprietaire(conv.id, 5) is True


def test_creer_conversation_prompt_nom_invalide():
    """Prompt inconnu (obtenir_id_par_nom -> None) → ValueError."""
    with patch.object(PromptDAO, "obtenir_id_par_nom", return_value=None):
        conv = Conversation(nom="Conv avec prompt inconnu", personnalisation="truc_bidon")
        with pytest.raises(ValueError):
            ConversationDAO.creer_conversation(conv)


def test_creer_conversation_prompt_id_valide():
    """personnalisation = int valide -> PromptDAO.existe_id retourne True."""
    with patch.object(PromptDAO, "existe_id", return_value=True):
        conv = Conversation(nom="Conv avec prompt id", personnalisation=3)
        conv = ConversationDAO.creer_conversation(conv)
        assert conv.personnalisation == 3


def test_creer_conversation_prompt_id_invalide():
    """personnalisation = int inexistant -> ValueError."""
    with patch.object(PromptDAO, "existe_id", return_value=False):
        conv = Conversation(nom="Conv avec mauvais prompt id", personnalisation=9999)
        with pytest.raises(ValueError):
            ConversationDAO.creer_conversation(conv)


def test_est_proprietaire_false_par_defaut():
    """Les conversations des données de test n'ont pas de proprietaire_id défini."""
    # Dans pop_db_test.sql les conversations initiales n'ont pas de proprietaire explicite
    assert ConversationDAO.est_proprietaire(1, 1) is False


def test_rechercher_mot_clef_titre():
    """Recherche par mot-clé dans le titre de conversation."""
    # user 9 participe aux conversations 1 et 3
    res = ConversationDAO.rechercher_mot_clef(id_user=9, mot_clef="recette")
    ids = [c.id for c in res]
    assert 1 in ids  # "Recette de pastèque au maroilles"


def test_rechercher_mot_clef_message():
    """Recherche par mot-clé dans le contenu des messages."""
    # user 10 participe à la conversation 2, où un message contient 'heureux'
    res = ConversationDAO.rechercher_mot_clef(id_user=10, mot_clef="heureux")
    assert len(res) >= 1
    assert res[0].id == 2


def test_rechercher_mot_clef_vide():
    """mot_clef vide ou espaces -> [] sans requête pertinente."""
    res = ConversationDAO.rechercher_mot_clef(id_user=10, mot_clef="   ")
    assert res == []


def test_rechercher_date_avec_date():
    """Recherche par date avec un objet date."""
    d = datetime.date(
        2025, 7, 21
    )  # il y a un message utilisateur pour conv 2 ce jour-là (user_id=10)
    res = ConversationDAO.rechercher_date(id_user=10, date=d)
    ids = [c.id for c in res]
    assert 2 in ids


def test_rechercher_date_avec_datetime():
    """Recherche par date avec un datetime -> normalisation au jour."""
    d = datetime.datetime(2025, 7, 21, 11, 0, 0)
    res = ConversationDAO.rechercher_date(id_user=10, date=d)
    ids = [c.id for c in res]
    assert 2 in ids


def test_rechercher_date_type_invalide():
    """Date invalide (string) -> Exception explicite."""
    with pytest.raises(Exception) as exc:
        ConversationDAO.rechercher_date(id_user=10, date="2025-07-21")
    assert "n'est pas au format datetime/date" in str(exc.value)


def test_rechercher_conv_mot_et_date_ok():
    """Recherche conjointe mot+date."""
    d = datetime.date(2025, 7, 21)
    res = ConversationDAO.rechercher_conv_mot_et_date(id_user=10, mot_cle="heureux", date=d)
    assert len(res) >= 1
    assert res[0].id == 2


def test_rechercher_conv_mot_et_date_date_invalide():
    """Date non date -> Exception."""
    with pytest.raises(Exception):
        ConversationDAO.rechercher_conv_mot_et_date(
            id_user=10, mot_cle="heureux", date="2025-07-21"
        )


def test_rechercher_conv_mot_et_date_mot_vide():
    """mot_cle vide -> [] immédiat."""
    d = datetime.date(2025, 7, 21)
    res = ConversationDAO.rechercher_conv_mot_et_date(id_user=10, mot_cle="   ", date=d)
    assert res == []


def test_lire_echanges_tout():
    """lire_echanges avec limit=None -> tous les messages en ordre chronologique."""
    echanges = ConversationDAO.lire_echanges(id_conv=2, offset=0, limit=None)
    # Dans les données de test, il y a 4 messages pour conv 2
    assert len(echanges) == 4
    # Le premier doit être le plus ancien
    assert echanges[0].id == 1
    # Le rôle affiché pour l'ia
    assert any(e.agent_name == "Assistant" for e in echanges)


def test_lire_echanges_pagine():
    """lire_echanges avec limit>0 -> pagination + reverse finale."""
    echanges = ConversationDAO.lire_echanges(id_conv=2, offset=0, limit=2)
    assert len(echanges) == 2
    # Même paginés, ils doivent être remontés dans l'ordre chronologique
    assert echanges[0].date_msg <= echanges[1].date_msg


def test_rechercher_echange_ok():
    """Recherche d'échanges par mot+date."""
    d = datetime.date(2025, 7, 21)
    res = ConversationDAO.rechercher_echange(conversation_id=2, mot_clef="heureux", date=d)
    assert len(res) == 1
    assert isinstance(res[0], Echange)
    assert "heureux" in res[0].message


def test_rechercher_echange_aucun():
    """Aucun échange -> Exception."""
    d = datetime.date(2025, 7, 21)
    with pytest.raises(Exception) as exc:
        ConversationDAO.rechercher_echange(conversation_id=2, mot_clef="foobar", date=d)
    assert "Aucun échange trouvé pour la conversation" in str(exc.value)


def test_ajouter_participant_ok():
    """Ajout d'un nouveau participant dans une conversation."""
    # conv 1 n'a pas encore user_id=1 comme participant
    res = ConversationDAO.ajouter_participant(conversation_id=1, id_user=1, role="membre")
    assert res is True


def test_ajouter_participant_deja_present():
    """Ajout d'un participant déjà présent -> Exception."""
    # On réutilise le couple (1,1) déjà ajouté
    with pytest.raises(Exception) as exc:
        ConversationDAO.ajouter_participant(conversation_id=1, id_user=1, role="membre")
    assert "est déjà participant de la conversation" in str(exc.value)


def test_retirer_participant_dernier():
    """Impossible de retirer le dernier participant d'une conversation."""
    # conv 5 n'a qu'un seul participant dans les données de test
    with pytest.raises(Exception) as exc:
        ConversationDAO.retirer_participant(conversation_id=5, id_user=5)
    assert "Impossible de retirer le dernier participant" in str(exc.value)


def test_retirer_participant_non_present():
    """Retrait d'un utilisateur non participant -> Exception."""
    # conv 1 a plusieurs participants, mais pas user_id=12345
    with pytest.raises(Exception) as exc:
        ConversationDAO.retirer_participant(conversation_id=1, id_user=12345)
    assert "n'est pas participant de la conversation" in str(exc.value)


def test_ajouter_echange_utilisateur_sans_user_id():
    """emetteur='utilisateur' mais utilisateur_id manquant -> Exception."""
    e = Echange(id=None, agent="user", message="Hello", date_msg="2025-05-09 14:56:33+00")
    # on force emetteur à 'utilisateur'
    setattr(e, "emetteur", "utilisateur")
    # utilisateur_id reste None
    with pytest.raises(Exception) as exc:
        ConversationDAO.ajouter_echange(1, e)
    assert "utilisateur_id requis" in str(exc.value)


def test_ajouter_echange_utilisateur_ok():
    """emetteur='utilisateur' avec utilisateur_id et participant existant -> insertion OK."""
    # Créer une nouvelle conversation
    conv = Conversation(nom="conv_test_user_msg")
    conv = ConversationDAO.creer_conversation(conv)

    # Ajouter l'utilisateur 9 comme participant à cette conversation
    ConversationDAO.ajouter_participant(conversation_id=conv.id, id_user=9, role="membre")

    # Créer un échange utilisateur cohérent
    e = Echange(id=None, agent="user", message="Coucou", date_msg="2025-05-09 14:56:33+00")
    setattr(e, "emetteur", "utilisateur")
    setattr(e, "utilisateur_id", 9)

    res = ConversationDAO.ajouter_echange(conv.id, e)

    assert res is True
    assert isinstance(e.id, int)
    assert res is True
    assert isinstance(e.id, int)


def test_mettre_a_j_preprompt_id_ok():
    """Mise à jour de prompt_id sur une conversation existante."""
    conv = Conversation(nom="conv_pour_prompt")
    conv = ConversationDAO.creer_conversation(conv)

    res = ConversationDAO.mettre_a_j_preprompt_id(conv.id, prompt_id=2)
    assert res == "personnalité modifié avec succès"

    conv_maj = ConversationDAO.trouver_par_id(conv.id)
    assert conv_maj.personnalisation == 2


def test_mettre_a_j_preprompt_id_fail():
    """Mise à jour d'une conversation inexistante -> Exception."""
    with pytest.raises(Exception) as exc:
        ConversationDAO.mettre_a_j_preprompt_id(999999, prompt_id=2)
    assert "Erreur dans la modification de la personnalisation" in str(exc.value)


def test_compter_conversations_user_3():
    """user_id=3 a exactement 1 conversation dans les données de test."""
    total = ConversationDAO.compter_conversations(3)
    assert total == 1


def test_compter_conversations_user_sans_conv():
    """Utilisateur sans conversation -> 0."""
    total = ConversationDAO.compter_conversations(9999)
    assert total == 0
