from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from src.business_object.conversation import Conversation
from src.business_object.echange import Echange
from src.dao.conversation_dao import ConversationDAO
from src.dao.prompt_dao import PromptDAO
from src.service.conversation_service import ConversationService, ErreurNonTrouvee, ErreurValidation

# Données factices
liste_conversations = [
    Conversation(id=1, nom="Projet IA", personnalisation="chatbot"),
    Conversation(id=2, nom="Discussion test", personnalisation="profil_test"),
    Conversation(id=3, nom="Sujet libre", personnalisation="assistant"),
]

echange1 = Echange(id=1, agent="user", message="Salut", date_msg=date.today())
echange2 = Echange(id=1, agent="assistant", message="Bonjour", date_msg=date.today())
liste_echanges = [echange1, echange2]


def test_creer_conv_titre_manquant():  # revoir
    """Création échouée car titre manquant"""

    # GIVEN
    titre, personnalisation, id_proprietaire = None, "chatbot", 2

    # WHEN / THEN
    try:
        ConversationService.creer_conv(titre, personnalisation, id_proprietaire)
        assert False, "ErreurValidation aurait dû être levée"
    except ErreurValidation as e:
        assert "titre" in str(e).lower()


def test_creer_conv_titre_trop_long():
    """Création échouée car titre trop long (>255)"""

    # GIVEN
    titre = "X" * 300
    personnalisation, id_proprietaire = "profil_test", 3

    # WHEN / THEN
    try:
        ConversationService.creer_conv(titre, personnalisation, id_proprietaire)
        assert False
    except ErreurValidation:
        assert True


def test_acceder_conversation_ok():
    """Accéder à une conversation existante"""

    # GIVEN
    conv = liste_conversations[0]
    ConversationDAO.trouver_par_id = MagicMock(return_value=conv)

    # WHEN
    resultat = ConversationService.acceder_conversation(1)

    # THEN
    assert resultat.nom == "Projet IA"


def test_acceder_conversation_introuvable():
    """Accès échoué car conversation introuvable"""

    # GIVEN
    ConversationDAO.trouver_par_id = MagicMock(return_value=None)

    # WHEN / THEN
    try:
        ConversationService.acceder_conversation(99)
        assert False
    except ErreurNonTrouvee:
        assert True


def test_renommer_conversation_ok():
    """Renommage réussi"""

    # GIVEN
    ConversationDAO.renommer_conv = MagicMock(return_value="titre modifié avec succès")
    # WHEN
    resultat = ConversationService.renommer_conversation(id_conversation=1, nouveau_titre="nouveau")

    # THEN
    assert resultat == "titre modifié avec succès"
    ConversationDAO.renommer_conv.assert_called_once_with(1, "nouveau")


def test_renommer_conversation_titre_vide():
    """Renommage échoué car titre vide"""

    # GIVEN

    # WHEN / THEN
    try:
        ConversationService.renommer_conversation(id_conversation=1, nouveau_titre="")
        assert False
    except ErreurValidation:
        assert True


def test_supprimer_conversation_ok():
    """Suppression réussie"""

    # GIVEN
    ConversationDAO.est_proprietaire = MagicMock(return_value=True)
    ConversationDAO.supprimer_conv = MagicMock(return_value=True)

    # WHEN
    resultat = ConversationService.supprimer_conversation(id_conversation=1, id_demandeur=10)

    # THEN
    assert resultat
    ConversationDAO.est_proprietaire.assert_called_once_with(1, 10)
    ConversationDAO.supprimer_conv.assert_called_once_with(id_conv=1)


def test_supprimer_conversation_id_manquant():
    """Suppression échouée car id manquant"""

    # GIVEN / WHEN / THEN
    try:
        ConversationService.supprimer_conversation(None, None)
        assert False
    except ErreurValidation:
        assert True


def test_lister_conversations_ok(monkeypatch):
    """Lister les conversations retourne bien une liste"""
    ConversationDAO.lister_conversations = MagicMock(return_value=liste_conversations)
    res = ConversationService.lister_conversations(10, limite=2)
    assert res == liste_conversations
    ConversationDAO.lister_conversations.assert_called_once_with(id_user=10, n=2)


def test_lister_conversations_aucune(monkeypatch):
    ConversationDAO.lister_conversations = MagicMock(return_value=[])
    res = ConversationService.lister_conversations(10, limite=5)
    assert res == []


def test_lister_conversations_limite_invalide():
    with pytest.raises(ErreurValidation):
        ConversationService.lister_conversations(10, limite=0)


liste_convs = [{"id": 1, "titre": "test"}]


def test_rechercher_conversations_ok():
    ConversationDAO.rechercher_conv_mot_et_date = MagicMock(return_value=liste_convs)

    res = ConversationService.rechercher_conversations(
        10, mot_cle="Conv", date_recherche=date.today()
    )

    assert res == liste_convs
    ConversationDAO.rechercher_conv_mot_et_date.assert_called_once_with(
        id_user=10, mot_cle="Conv", date=date.today()
    )


def test_rechercher_conversations_aucune():
    ConversationDAO.rechercher_conv_mot_et_date = MagicMock(return_value=[])
    res = ConversationService.rechercher_conversations(10, mot_cle="X", date_recherche=date.today())
    assert res == []


def test_lire_fil_ok():
    ConversationDAO.lire_echanges = MagicMock(return_value=liste_echanges)

    res = ConversationService.lire_fil(1, decalage=0, limite=10)

    assert res == liste_echanges
    ConversationDAO.lire_echanges.assert_called_once_with(1, offset=0, limit=10)


def test_rechercher_message_ok():
    ConversationDAO.rechercher_echange = MagicMock(return_value=[echange1])

    res = ConversationService.rechercher_message(1, mot_cle="Salut", date_recherche=None)

    assert res == [echange1]
    ConversationDAO.rechercher_echange.assert_called_once_with(1, "Salut", None)


def test_rechercher_message_ko():
    with pytest.raises(ErreurValidation):
        ConversationService.rechercher_message(1, mot_cle=None, date_recherche=None)


def test_ajouter_utilisateur_ok():
    ConversationDAO.est_proprietaire = MagicMock(return_value=True)
    ConversationDAO.ajouter_participant = MagicMock(return_value=True)

    assert ConversationService.ajouter_utilisateur(1, 10, "membre", id_demandeur=10) is True

    ConversationDAO.est_proprietaire.assert_called_once_with(1, 10)
    ConversationDAO.ajouter_participant.assert_called_once_with(1, 10, "membre")


def test_ajouter_utilisateur_invalide():
    with pytest.raises(ErreurValidation):
        ConversationService.ajouter_utilisateur(None, 10, "membre", id_demandeur=10)


def test_retirer_utilisateur_ok():
    ConversationDAO.est_proprietaire = MagicMock(return_value=True)
    ConversationDAO.retirer_participant = MagicMock(return_value=True)

    assert ConversationService.retirer_utilisateur(1, 10, id_demandeur=10) is True

    ConversationDAO.est_proprietaire.assert_called_once_with(1, 10)
    ConversationDAO.retirer_participant.assert_called_once_with(1, 10)


def test_retirer_utilisateur_invalide():
    with pytest.raises(ErreurValidation):
        ConversationService.retirer_utilisateur(1, None, id_demandeur=10)


def test_mettre_a_jour_personnalisation_ok():
    # GIVEN
    PromptDAO.get_id_by_name = MagicMock(return_value=123)
    ConversationDAO.mettre_a_j_preprompt_id = MagicMock(return_value=True)
    service = ConversationService()

    # WHEN/THEN
    assert service.mettre_a_jour_personnalisation(1, "NouveauProfil") is True
    PromptDAO.get_id_by_name.assert_called_once_with("NouveauProfil")
    ConversationDAO.mettre_a_j_preprompt_id.assert_called_once_with(1, 123)


def test_mettre_a_jour_personnalisation_invalide():
    service = ConversationService()
    with pytest.raises(ErreurValidation):
        service.mettre_a_jour_personnalisation(1, None)


def test_demander_assistant_ok():
    # On patch la classe LLM_API dans le module où elle est définie
    with patch("src.client.llm_client.LLM_API") as MockLLM:
        mock_client = MockLLM.return_value
        # generate() renvoie simplement une string contenant "Bonjour"
        mock_client.generate.return_value = "Bonjour, je suis l'assistant !"

        e = ConversationService.demander_assistant("Bonjour")

        assert e is not None
        assert e.agent == "assistant"
        assert "Bonjour" in e.message
        mock_client.generate.assert_called_once()
