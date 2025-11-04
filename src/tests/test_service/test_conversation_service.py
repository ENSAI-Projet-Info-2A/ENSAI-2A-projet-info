import pytest
from datetime import date
from unittest.mock import MagicMock

from service.conversation_service.py import (
    ConversationService,
    ErreurValidation,
    ErreurNonTrouvee
)


# --- Fixtures ---

@pytest.fixture
def dao_simule():
    """Crée un DAO simulé avec des méthodes factices."""
    dao = MagicMock()
    dao.creer_conversation.return_value = MagicMock(id=1, titre="Test", personnalisation="Général")
    dao.obtenir_conversation.return_value = MagicMock(id=1, titre="Test")
    dao.renommer_conversation.return_value = True
    dao.supprimer_conversation.return_value = True
    dao.lister_conversations.return_value = ["conv1", "conv2"]
    dao.rechercher_conversations.return_value = ["conv_recherche"]
    dao.lire_fil.return_value = ["msg1", "msg2"]
    dao.rechercher_message.return_value = ["msg_trouve"]
    dao.ajouter_utilisateur.return_value = True
    dao.retirer_utilisateur.return_value = True
    dao.mettre_a_jour_personnalisation.return_value = True
    return dao


@pytest.fixture
def service(dao_simule):
    """Crée une instance du service avec un DAO simulé."""
    return ConversationService(dao_simule)


# --- Tests de création ---

def test_creer_conversation_valide(service):
    conv = service.creer_conversation("Discussion test", "Profil A", 1)
    assert conv.id == 1
    service.dao.creer_conversation.assert_called_once()

def test_creer_conversation_sans_titre(service):
    with pytest.raises(ErreurValidation):
        service.creer_conversation(None, "Profil", 1)

def test_creer_conversation_titre_trop_long(service):
    titre_trop_long = "x" * 300
    with pytest.raises(ErreurValidation):
        service.creer_conversation(titre_trop_long, "Profil", 1)

def test_creer_conversation_sans_personnalisation(service):
    with pytest.raises(ErreurValidation):
        service.creer_conversation("Titre", None, 1)


# --- Tests d'accès ---

def test_acceder_conversation_valide(service):
    conv = service.acceder_conversation(1)
    assert conv.id == 1
    service.dao.obtenir_conversation.assert_called_once_with(1)

def test_acceder_conversation_non_trouvee(service):
    service.dao.obtenir_conversation.return_value = None
    with pytest.raises(ErreurNonTrouvee):
        service.acceder_conversation(999)


# --- Tests de renommage ---

def test_renommer_conversation_valide(service):
    assert service.renommer_conversation(1, "Nouveau nom") is True

def test_renommer_conversation_sans_nom(service):
    with pytest.raises(ErreurValidation):
        service.renommer_conversation(1, "")

def test_renommer_conversation_sans_id(service):
    with pytest.raises(ErreurValidation):
        service.renommer_conversation(None, "Nom")


# --- Tests de suppression ---

def test_supprimer_conversation_valide(service):
    assert service.supprimer_conversation(1) is True

def test_supprimer_conversation_sans_id(service):
    with pytest.raises(ErreurValidation):
        service.supprimer_conversation(None)


# --- Tests de liste ---

def test_lister_conversations(service):
    resultat = service.lister_conversations(1, 10)
    assert resultat == ["conv1", "conv2"]

def test_lister_conversations_id_manquant(service):
    with pytest.raises(ErreurValidation):
        service.lister_conversations(None, 10)

def test_lister_conversations_limite_invalide(service):
    with pytest.raises(ErreurValidation):
        service.lister_conversations(1, 0)


# --- Tests de recherche ---

def test_rechercher_conversations(service):
    result = service.rechercher_conversations(1, "mot", date.today())
    assert "conv_recherche" in result

def test_rechercher_conversations_sans_id(service):
    with pytest.raises(ErreurValidation):
        service.rechercher_conversations(None, "mot", date.today())


# --- Tests d'ajout / retrait d'utilisateurs ---

def test_ajouter_utilisateur_valide(service):
    assert service.ajouter_utilisateur(1, 2, "membre") is True

def test_ajouter_utilisateur_invalide(service):
    with pytest.raises(ErreurValidation):
        service.ajouter_utilisateur(1, None, "membre")

def test_retirer_utilisateur_valide(service):
    assert service.retirer_utilisateur(1, 2) is True

def test_retirer_utilisateur_invalide(service):
    with pytest.raises(ErreurValidation):
        service.retirer_utilisateur(None, 2)


# --- Tests de mise à jour de personnalisation ---

def test_mettre_a_jour_personnalisation(service):
    assert service.mettre_a_jour_personnalisation(1, "profil B") is True

def test_mettre_a_jour_personnalisation_sans_id(service):
    with pytest.raises(ErreurValidation):
        service.mettre_a_jour_personnalisation(None, "profil B")


# --- Tests d'exportation (JSON simulé) ---

def test_exporter_conversation_json(service, tmp_path):
    chemin = tmp_path / "conversation_1.json"
    service.dao.lire_fil.return_value = []
    assert service.exporter_conversation(1, "json") is True

def test_exporter_conversation_format_invalide(service):
    with pytest.raises(ErreurValidation):
        service.exporter_conversation(1, "xml")


# --- Tests de l'assistant ---

def test_demander_assistant_valide(service):
    echange = service.demander_assistant("Bonjour !")
    assert "réponse simulée" in echange.message

def test_demander_assistant_vide(service):
    with pytest.raises(ErreurValidation):
        service.demander_assistant("")
