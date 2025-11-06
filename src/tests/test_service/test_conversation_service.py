import pytest
from datetime import datetime, date
from unittest.mock import MagicMock
from service.conversation_service import ConversationService, ErreurValidation, ErreurNonTrouvee
from business_object.conversation import Conversation
from dao.conversation_dao import ConversationDAO
from business_object.echange import Echange


# Données factices
liste_conversations = [
    Conversation(id=1, nom="Projet IA", personnalisation="chatbot"),
    Conversation(id=2, nom="Discussion test", personnalisation="profil_test"),
    Conversation(id=3, nom="Sujet libre", personnalisation="assistant"),
]

echange1 = Echange(id=1, agent="user", message="Salut", date_msg=date.today())
echange2 = Echange(id=1, agent="assistant", message="Bonjour", date_msg=date.today())
liste_echanges = [echange1, echange2]


def test_creer_conv_titre_manquant(): #revoir
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
    ConversationDAO.supprimer_conv = MagicMock(return_value=True)

    # WHEN
    resultat = ConversationService.supprimer_conversation(id_conversation=1)

    # THEN
    assert resultat
    ConversationDAO.supprimer_conv.assert_called_once_with(id_conv=1)


def test_supprimer_conversation_id_manquant():
    """Suppression échouée car id manquant"""

    # GIVEN / WHEN / THEN
    try:
        ConversationService.supprimer_conversation(None)
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
    ConversationDAO.rechercher_conv_motC_et_date = MagicMock(return_value=liste_convs)
    res = ConversationService.rechercher_conversations(10, mot_cle="Conv", date_recherche=date.today())
    assert res == liste_convs
    ConversationDAO.rechercher_conv_motC_et_date.assert_called_once()


def test_rechercher_conversations_aucune():
    ConversationDAO.rechercher_conv_motC_et_date = MagicMock(return_value=[])
    res = ConversationService.rechercher_conversations(10, mot_cle="X", date_recherche=date.today())
    assert res == []


def test_lire_fil_ok():
    ConversationDAO.lire_echanges = MagicMock(return_value=liste_echanges)
    res = ConversationService.lire_fil(1, decalage=0, limite=10)
    assert res == liste_echanges
    ConversationDAO.lire_echanges.assert_called_once_with(1, 10)


def test_rechercher_message_ok():
    ConversationDAO.rechercher_message = MagicMock(return_value=[echange1])
    res = ConversationService.rechercher_message(1, mot_cle="Salut", date_recherche=None)
    assert res == [echange1]


def test_rechercher_message_ko():
    with pytest.raises(ErreurValidation):
        ConversationService.rechercher_message(1, mot_cle=None, date_recherche=None)


def test_ajouter_utilisateur_ok():
    ConversationDAO.ajouter_utilisateur = MagicMock(return_value=True)
    assert ConversationService.ajouter_utilisateur(1, 10, "membre") is True


def test_ajouter_utilisateur_invalide():
    with pytest.raises(ErreurValidation):
        ConversationService.ajouter_utilisateur(None, 10, "membre")


def test_retirer_utilisateur_ok():
    ConversationDAO.retirer_utilisateur = MagicMock(return_value=True)
    assert ConversationService.retirer_utilisateur(1, 10) is True


def test_retirer_utilisateur_invalide():
    with pytest.raises(ErreurValidation):
        ConversationService.retirer_utilisateur(1, None)


def test_mettre_a_jour_personnalisation_ok():
    # GIVEN
    ConversationDAO.mettre_a_jour_personnalisation = MagicMock(return_value=True)
    service = ConversationService()  # Créer une instance
    
    # WHEN/THEN
    assert service.mettre_a_jour_personnalisation(1, "NouveauProfil") is True

def test_mettre_a_jour_personnalisation_invalide():
    with pytest.raises(ErreurValidation):
        ConversationService.mettre_a_jour_personnalisation(1, "")


def test_demander_assistant_ok():
    # WHEN
    e = ConversationService.demander_assistant("Bonjour")
    
    # THEN
    assert e is not None
    assert e.agent == "assistant"
    assert "Bonjour" in e.message