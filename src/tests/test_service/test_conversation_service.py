from unittest.mock import MagicMock
from service.conversation_service import ConversationService, ErreurValidation, ErreurNonTrouvee
from business_object.conversation import Conversation
from dao.conversation_dao import ConversationDAO


# Données factices
liste_conversations = [
    Conversation(id=1, nom="Projet IA", personnalisation="chatbot", id_proprietaire=2),
    Conversation(id=2, nom="Discussion test", personnalisation="profil_test", id_proprietaire=3),
    Conversation(id=3, nom="Sujet libre", personnalisation="assistant", id_proprietaire=4),
]


# ----------------- TEST creer_conv -----------------



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


# ----------------- TEST accéder conversation -----------------
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


# ----------------- TEST renommer_conversation -----------------
def test_renommer_conversation_ok():
    """Renommage réussi"""

    # GIVEN
    ConversationDAO.renommer_conversation = MagicMock(return_value=True)
    id_conv, nouveau_titre = 1, "Nouveau titre"

    # WHEN
    resultat = ConversationService.renommer_conversation(id_conv, nouveau_titre)

    # THEN
    assert resultat
    ConversationDAO.renommer_conversation.assert_called_once_with(id_conv, nouveau_titre)


def test_renommer_conversation_titre_vide():
    """Renommage échoué car titre vide"""

    # GIVEN
    id_conv, nouveau_titre = 1, " "

    # WHEN / THEN
    try:
        ConversationService.renommer_conversation(id_conv, nouveau_titre)
        assert False
    except ErreurValidation:
        assert True


# ----------------- TEST supprimer_conversation -----------------
def test_supprimer_conversation_ok():
    """Suppression réussie"""

    # GIVEN
    ConversationDAO.supprimer_conv = MagicMock(return_value=True)

    # WHEN
    resultat = ConversationService.supprimer_conversation(1)

    # THEN
    assert resultat
    ConversationDAO.supprimer_conv.assert_called_once_with(1)


def test_supprimer_conversation_id_manquant():
    """Suppression échouée car id manquant"""

    # GIVEN / WHEN / THEN
    try:
        ConversationService.supprimer_conversation(None)
        assert False
    except ErreurValidation:
        assert True
