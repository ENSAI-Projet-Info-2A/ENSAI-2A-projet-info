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

echange1 = Echange(id_conversation=1, expediteur="user", message="Salut", date_echange=date.today())
echange2 = Echange(id_conversation=1, expediteur="assistant", message="Bonjour", date_echange=date.today())
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

def test_lister_conversations_ok(monkeypatch):
    """Lister les conversations retourne bien une liste"""
    ConversationDAO.lister_conversations = MagicMock(return_value=liste_convs)
    res = ConversationService.lister_conversations(10, limite=2)
    assert res == liste_convs
    ConversationDAO.lister_conversations.assert_called_once_with(id_user=10, n=2)

def test_lister_conversations_aucune(monkeypatch):
    ConversationDAO.lister_conversations = MagicMock(return_value=[])
    res = ConversationService.lister_conversations(10, limite=5)
    assert res is None  # Pas de conversation trouvée

def test_lister_conversations_limite_invalide():
    with pytest.raises(ErreurValidation):
        ConversationService.lister_conversations(10, limite=0)

def test_rechercher_conversations_ok():
    ConversationDAO.rechercher_conversation = MagicMock(return_value=liste_convs)
    res = ConversationService.rechercher_conversations(10, mot_cle="Conv", date_recherche=date.today())
    assert res == liste_convs
    ConversationDAO.rechercher_conversation.assert_called_once()

def test_rechercher_conversations_aucune():
    ConversationDAO.rechercher_conversation = MagicMock(return_value=[])
    res = ConversationService.rechercher_conversations(10, mot_cle="X", date_recherche=date.today())
    assert res is None

def test_lire_fil_ok():
    ConversationDAO.lire_fil = MagicMock(return_value=liste_echanges)
    res = ConversationService.lire_fil(1, decalage=0, limite=10)
    assert res == liste_echanges
    ConversationDAO.lire_fil.assert_called_once_with(1, 0, 10)


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
    ConversationDAO.mettre_a_jour_personnalisation = MagicMock(return_value=True)
    assert ConversationService.mettre_a_jour_personnalisation(1, "NouveauProfil") is True

def test_mettre_a_jour_personnalisation_invalide():
    with pytest.raises(ErreurValidation):
        ConversationService.mettre_a_jour_personnalisation(1, "")

def test_demander_assistant_ok():
    e = ConversationService.demander_assistant("Bonjour")
    assert e.message.startswith("Voici une réponse simulée")
    assert e.expediteur == "assistant"
