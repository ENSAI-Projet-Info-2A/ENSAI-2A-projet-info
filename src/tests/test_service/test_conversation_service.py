from datetime import date
from datetime import datetime as Date
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


def test_resoudre_id_prompt_aucun():
    """personnalisation = None ou '' → None."""
    assert ConversationService._resoudre_id_prompt(None) is None
    assert ConversationService._resoudre_id_prompt("   ") is None


def test_resoudre_id_prompt_int_valide():
    """personnalisation = int existant → renvoyé tel quel."""
    with patch.object(PromptDAO, "existe_id", return_value=True) as mock_existe:
        res = ConversationService._resoudre_id_prompt(42)
        assert res == 42
        mock_existe.assert_called_once_with(42)


def test_resoudre_id_prompt_int_inexistant():
    """personnalisation = int inexistant → ErreurValidation."""
    with patch.object(PromptDAO, "existe_id", return_value=False):
        with pytest.raises(ErreurValidation):
            ConversationService._resoudre_id_prompt(9999)


def test_resoudre_id_prompt_nom_valide():
    """personnalisation = str connue → résolue via obtenir_id_par_nom."""
    with patch.object(PromptDAO, "obtenir_id_par_nom", return_value=7) as mock_get:
        res = ConversationService._resoudre_id_prompt("profil_test")
        assert res == 7
        mock_get.assert_called_once_with("profil_test")


def test_resoudre_id_prompt_nom_inconnu():
    """personnalisation = str inconnue → ErreurValidation."""
    with patch.object(PromptDAO, "obtenir_id_par_nom", return_value=None):
        with pytest.raises(ErreurValidation):
            ConversationService._resoudre_id_prompt("prompt_qui_n_existe_pas")


def test_resoudre_prompt_systeme_sans_id():
    """Sans id_conversation → on retourne le DEFAULT_SYSTEM_PROMPT."""
    res = ConversationService._resoudre_prompt_systeme_pour_conv(None)
    assert res == ConversationService.DEFAULT_SYSTEM_PROMPT


def test_resoudre_prompt_systeme_conv_sans_prompt():
    """Conversation trouvée mais sans personnalisation → prompt par défaut."""
    conv = Conversation(id=1, nom="Test", personnalisation=None)
    with patch.object(ConversationDAO, "trouver_par_id", return_value=conv):
        res = ConversationService._resoudre_prompt_systeme_pour_conv(1)
        assert res == ConversationService.DEFAULT_SYSTEM_PROMPT


def test_resoudre_prompt_systeme_conv_avec_prompt():
    """Conversation avec prompt_id → texte renvoyé par PromptDAO."""
    conv = Conversation(id=1, nom="Test", personnalisation=3)
    with (
        patch.object(ConversationDAO, "trouver_par_id", return_value=conv),
        patch.object(PromptDAO, "obtenir_texte_prompt_par_id", return_value="TEXTE_PROMPT"),
    ):
        res = ConversationService._resoudre_prompt_systeme_pour_conv(1)
        assert res == "TEXTE_PROMPT"


def test_resoudre_prompt_systeme_exception():
    """En cas d'exception, on retombe sur le prompt par défaut."""
    with patch.object(ConversationDAO, "trouver_par_id", side_effect=Exception("DB down")):
        res = ConversationService._resoudre_prompt_systeme_pour_conv(1)
        assert res == ConversationService.DEFAULT_SYSTEM_PROMPT


def test_resoudre_prompt_systeme_aucun_id():
    res = ConversationService._resoudre_prompt_systeme_pour_conv(None)
    assert res == ConversationService.DEFAULT_SYSTEM_PROMPT


def test_resoudre_prompt_systeme_conv_sans_personnalisation():
    conv = Conversation(id=1, nom="Test", personnalisation=None)
    with patch("src.dao.conversation_dao.ConversationDAO.trouver_par_id", return_value=conv):
        res = ConversationService._resoudre_prompt_systeme_pour_conv(1)
        assert res == ConversationService.DEFAULT_SYSTEM_PROMPT


def test_resoudre_prompt_systeme_erreur_dao():
    with patch("src.dao.conversation_dao.ConversationDAO.trouver_par_id", side_effect=Exception):
        res = ConversationService._resoudre_prompt_systeme_pour_conv(1)
        assert res == ConversationService.DEFAULT_SYSTEM_PROMPT


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


def test_rechercher_conversations_mot_et_date():
    """mot_cle + date → ConversationDAO.rechercher_conv_mot_et_date appelé."""
    liste_conversations = ["conv1", "conv2"]

    with patch.object(
        ConversationDAO,
        "rechercher_conv_mot_et_date",
        return_value=liste_conversations,
    ) as mock:
        res = ConversationService.rechercher_conversations(
            id_utilisateur=1,
            mot_cle="test",
            date_recherche=date(2025, 1, 1),
        )

    assert res == liste_conversations
    mock.assert_called_once_with(
        id_user=1,
        mot_cle="test",
        date=date(2025, 1, 1),
    )


def test_rechercher_conversations_mot_seul():
    """mot_cle seul → ConversationDAO.rechercher_mot_clef."""
    with patch.object(
        ConversationDAO, "rechercher_mot_clef", return_value=liste_conversations
    ) as mock:
        res = ConversationService.rechercher_conversations(
            id_utilisateur=1,
            mot_cle="ia",
            date_recherche=None,
        )
        assert res == liste_conversations
        mock.assert_called_once()


def test_rechercher_conversations_date_seule():
    """date seule → ConversationDAO.rechercher_date."""
    d = date(2025, 1, 1)
    with patch.object(ConversationDAO, "rechercher_date", return_value=liste_conversations) as mock:
        res = ConversationService.rechercher_conversations(
            id_utilisateur=1,
            mot_cle=None,
            date_recherche=d,
        )
        assert res == liste_conversations
        mock.assert_called_once_with(id_user=1, date=d)


def test_rechercher_conversations_sans_critere():
    """Sans mot_cle ni date → ConversationDAO.lister_conversations."""
    with patch.object(
        ConversationDAO, "lister_conversations", return_value=liste_conversations
    ) as mock:
        res = ConversationService.rechercher_conversations(
            id_utilisateur=1,
            mot_cle=None,
            date_recherche=None,
        )
        assert res == liste_conversations
        mock.assert_called_once_with(id_user=1)


def test_rechercher_conversations_id_utilisateur_manquant():
    """id_utilisateur None → ErreurValidation."""
    with pytest.raises(ErreurValidation):
        ConversationService.rechercher_conversations(
            id_utilisateur=None,
            mot_cle="test",
            date_recherche=None,
        )


def test_lire_fil_ok():
    ConversationDAO.lire_echanges = MagicMock(return_value=liste_echanges)

    res = ConversationService.lire_fil(1, decalage=0, limite=10)

    assert res == liste_echanges
    ConversationDAO.lire_echanges.assert_called_once_with(1, offset=0, limit=10)


def test_lire_fil_id_conversation_manquant():
    """id_conversation None → ErreurValidation."""
    with pytest.raises(ErreurValidation):
        ConversationService.lire_fil(None, decalage=0, limite=10)


def test_lire_fil_limite_none():
    """limite=None → ConversationDAO.lire_echanges appelé avec limit=None."""
    with patch.object(ConversationDAO, "lire_echanges", return_value=liste_echanges) as mock:
        res = ConversationService.lire_fil(1, decalage=5, limite=None)

        assert res == liste_echanges
        mock.assert_called_once_with(1, offset=5, limit=None)


def test_lire_fil_decalage_negatif():
    """decalage < 0 → offset normalisé à 0."""
    with patch.object(ConversationDAO, "lire_echanges", return_value=liste_echanges) as mock:
        res = ConversationService.lire_fil(1, decalage=-10, limite=3)

        assert res == liste_echanges
        mock.assert_called_once_with(1, offset=0, limit=3)


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
    PromptDAO.obtenir_id_par_nom = MagicMock(return_value=123)
    ConversationDAO.mettre_a_j_preprompt_id = MagicMock(return_value=True)
    service = ConversationService()

    # WHEN/THEN
    assert service.mettre_a_jour_personnalisation(1, "NouveauProfil") is True
    PromptDAO.obtenir_id_par_nom.assert_called_once_with("NouveauProfil")
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


# ---------------------------------------------------------------------------
#   NOUVEAUX TESTS AJOUTÉS POUR AMÉLIORER LA COUVERTURE DE ConversationService
#   (Pas dans un odre de rangement logique car on a pas eu le temps de les 
#    réaranger)
# ---------------------------------------------------------------------------


def test_acceder_conversation_id_manquant():
    """id_conversation None → ErreurValidation."""
    with pytest.raises(ErreurValidation):
        ConversationService.acceder_conversation(None)


def test_renommer_conversation_id_manquant():
    """Renommage échoué car id_conversation manquant."""
    with pytest.raises(ErreurValidation):
        ConversationService.renommer_conversation(None, "nouveau")


def test_supprimer_conversation_non_proprietaire():
    """Suppression refusée si l'utilisateur n'est pas propriétaire."""
    ConversationDAO.est_proprietaire = MagicMock(return_value=False)
    with pytest.raises(ErreurValidation):
        ConversationService.supprimer_conversation(1, id_demandeur=10)


def test_creer_conv_ok_sans_proprietaire():
    """Création de conversation sans propriétaire (cas nominal simple)."""
    conv = Conversation(id=1, nom="Projet IA", personnalisation=None)
    ConversationDAO.creer_conversation = MagicMock(return_value=conv)

    msg = ConversationService.creer_conv("Projet IA", None, id_proprietaire=None)

    assert "Conversation" in msg
    assert "créée" in msg
    ConversationDAO.creer_conversation.assert_called_once()


def test_creer_conv_avec_proprietaire_echec_ajout_participant():
    """On log l'erreur d'ajout de participant mais la création reste OK."""
    conv = Conversation(id=1, nom="Projet IA", personnalisation=None)
    ConversationDAO.creer_conversation = MagicMock(return_value=conv)
    ConversationDAO.ajouter_participant = MagicMock(side_effect=Exception("Erreur d'ajout"))

    msg = ConversationService.creer_conv("Projet IA", None, id_proprietaire=10)

    assert "Conversation" in msg
    ConversationDAO.creer_conversation.assert_called_once()


def test_lister_conversations_id_utilisateur_manquant():
    """id_utilisateur None → ErreurValidation."""
    with pytest.raises(ErreurValidation):
        ConversationService.lister_conversations(None)


def test_lister_conversations_exception_aucune():
    """Exception 'Aucune conversation trouvée' → retour liste vide."""
    ConversationDAO.lister_conversations = MagicMock(
        side_effect=Exception("Aucune conversation trouvée")
    )
    res = ConversationService.lister_conversations(10)
    assert res == []


def test_rechercher_conversations_exception_aucune():
    """Exception contenant 'aucune conversation' → retour []."""
    ConversationDAO.rechercher_mot_clef = MagicMock(side_effect=Exception("Aucune conversation"))
    res = ConversationService.rechercher_conversations(10, mot_cle="x", date_recherche=None)
    assert res == []


def test_rechercher_conversations_exception_autre():
    """Autre exception → propagée."""
    ConversationDAO.rechercher_mot_clef = MagicMock(side_effect=Exception("bug interne"))
    with pytest.raises(Exception):
        ConversationService.rechercher_conversations(10, mot_cle="x", date_recherche=None)


def test_lire_fil_exception():
    """Erreur DAO lors de la lecture du fil → exception propagée."""
    ConversationDAO.lire_echanges = MagicMock(side_effect=Exception("db down"))
    with pytest.raises(Exception):
        ConversationService.lire_fil(1)


def test_rechercher_message_id_conversation_manquant():
    """Recherche de messages sans id_conversation → ErreurValidation."""
    with pytest.raises(ErreurValidation):
        ConversationService.rechercher_message(None, mot_cle="x", date_recherche=None)


def test_rechercher_message_aucun_resultat():
    """Si aucun message trouvé, la fonction retourne None."""
    ConversationDAO.rechercher_echange = MagicMock(return_value=[])
    res = ConversationService.rechercher_message(1, mot_cle="Salut", date_recherche=None)
    assert res is None


def test_ajouter_utilisateur_non_proprietaire():
    """Seul le propriétaire peut ajouter un utilisateur."""
    ConversationDAO.est_proprietaire = MagicMock(return_value=False)
    with pytest.raises(ErreurValidation):
        ConversationService.ajouter_utilisateur(1, 10, "membre", id_demandeur=20)


def test_retirer_utilisateur_non_proprietaire():
    """Seul le propriétaire peut retirer un utilisateur."""
    ConversationDAO.est_proprietaire = MagicMock(return_value=False)
    with pytest.raises(ErreurValidation):
        ConversationService.retirer_utilisateur(1, 10, id_demandeur=20)


def test_retirer_utilisateur_aucun_trouve():
    """Si retirer_participant retourne False → None renvoyé."""
    ConversationDAO.est_proprietaire = MagicMock(return_value=True)
    ConversationDAO.retirer_participant = MagicMock(return_value=False)

    res = ConversationService.retirer_utilisateur(1, 10, id_demandeur=10)

    assert res is None
    ConversationDAO.retirer_participant.assert_called_once_with(1, 10)


def test_mettre_a_jour_personnalisation_id_manquant():
    """Mise à jour de personnalisation sans id_conversation → ErreurValidation."""
    service = ConversationService()
    with pytest.raises(ErreurValidation):
        service.mettre_a_jour_personnalisation(None, "Profil")


def test_mettre_a_jour_personnalisation_exception_dao():
    """Erreur DAO lors de la mise à jour → exception propagée."""
    service = ConversationService()
    ConversationService._resoudre_id_prompt = MagicMock(return_value=42)
    ConversationDAO.mettre_a_j_preprompt_id = MagicMock(side_effect=Exception("db"))

    with pytest.raises(Exception):
        service.mettre_a_jour_personnalisation(1, "Profil")


def test_exporter_conversation_format_invalide():
    """Format non supporté → ErreurValidation."""
    service = ConversationService()
    with pytest.raises(ErreurValidation):
        service.exporter_conversation(1, "pdf")


def test_exporter_conversation_id_manquant():
    """Export sans id_conversation → ErreurValidation."""
    service = ConversationService()
    with pytest.raises(ErreurValidation):
        service.exporter_conversation(None, "json")


def test_exporter_conversation_json(tmp_path, monkeypatch):
    """Export JSON nominal : fichier créé dans exports/."""
    # On travaille dans un répertoire temporaire
    monkeypatch.chdir(tmp_path)

    ConversationDAO.lire_echanges = MagicMock(return_value=liste_echanges)
    conv = Conversation(id=1, nom="Test", personnalisation=None)
    setattr(conv, "date_creation", Date.today())
    ConversationDAO.trouver_par_id = MagicMock(return_value=conv)

    service = ConversationService()
    assert service.exporter_conversation(1, "json") is True

    fichier = tmp_path / "exports" / "conversation_1.json"
    assert fichier.exists()


def test_exporter_conversation_txt_sans_conv(tmp_path, monkeypatch):
    """Export TXT quand la conversation n'est pas retrouvée (fallback titre générique)."""
    monkeypatch.chdir(tmp_path)

    ConversationDAO.lire_echanges = MagicMock(return_value=[])
    ConversationDAO.trouver_par_id = MagicMock(side_effect=Exception("introuvable"))

    service = ConversationService()
    assert service.exporter_conversation(2, "txt") is True

    fichier = tmp_path / "exports" / "conversation_2.txt"
    assert fichier.exists()


def test_demander_assistant_message_vide():
    """Message vide → ErreurValidation."""
    with pytest.raises(ErreurValidation):
        ConversationService.demander_assistant("   ")


def test_demander_assistant_avec_conversation_et_persistance(monkeypatch):
    """
    Cas complet :
    - options personnalisées
    - historique existant
    - persistance des échanges activée
    """
    with patch("src.client.llm_client.LLM_API") as MockLLM:
        mock_client = MockLLM.return_value
        # Réponse de type Echange (pas juste une string)
        rep = Echange(agent="assistant", message="Réponse détaillée", date_msg=Date.today())
        mock_client.generate.return_value = rep

        # Prompt système simplifié
        monkeypatch.setattr(
            ConversationService,
            "_resoudre_prompt_systeme_pour_conv",
            lambda _id: "PROMPT_SYSTEME",
        )

        # Historique ancien
        ancien1 = Echange(agent="user", message="ancien msg", date_msg=Date.today())
        setattr(ancien1, "expediteur", "utilisateur")
        ancien2 = Echange(agent="assistant", message="ancien rep", date_msg=Date.today())
        setattr(ancien2, "emetteur", "ia")

        ConversationDAO.lire_echanges = MagicMock(return_value=[ancien1, ancien2])
        ConversationDAO.ajouter_echange = MagicMock(return_value=True)

        e = ConversationService.demander_assistant(
            "Bonjour",
            options={"temperature": 0.5, "top_p": 0.9, "max_tokens": 50, "stop": "\n"},
            id_conversation=1,
            id_user=99,
        )

        assert e.agent == "assistant"
        assert "Réponse" in e.message

        # On a bien persisté les deux échanges (user + assistant)
        assert ConversationDAO.ajouter_echange.call_count == 2

        # Vérifier la taille de l'historique passé au LLM
        args, kwargs = mock_client.generate.call_args
        history = kwargs.get("history") or args[0]
        # 1 system + 2 anciens + 1 nouveau user
        assert len(history) == 4

def test_exporter_conversation_txt_avec_echanges(tmp_path, monkeypatch):
    """
    Couvre la boucle sur les échanges dans exporter_conversation (format TXT),
    avec les deux cas :
    - echange qui a afficher_echange()
    - echange qui n'a PAS afficher_echange (fallback formatage date/agent/message)
    """
    monkeypatch.chdir(tmp_path)

    # 1) Premier échange avec méthode afficher_echange()
    class EchangeAffichable:
        def __init__(self):
            self._txt = "LIGNE_FORMATTEE"

        def afficher_echange(self):
            return self._txt

    e1 = EchangeAffichable()

    # 2) Deuxième échange sans afficher_echange, mais avec date_msg / agent_name / message
    class EchangeBrut:
        def __init__(self):
            self.date_msg = Date(2025, 1, 1, 12, 0, 0)
            self.agent_name = "User"
            self.message = "Bonjour"

    e2 = EchangeBrut()

    # On renvoie ces deux échanges
    ConversationDAO.lire_echanges = MagicMock(return_value=[e1, e2])

    # Conversation avec nom et date_creation
    conv = Conversation(id=3, nom="Sujet libre", personnalisation=None)
    setattr(conv, "date_creation", Date(2025, 1, 1, 10, 0, 0))
    ConversationDAO.trouver_par_id = MagicMock(return_value=conv)

    service = ConversationService()
    assert service.exporter_conversation(3, "txt") is True

    fichier = tmp_path / "exports" / "conversation_3.txt"
    assert fichier.exists()

    contenu = fichier.read_text(encoding="utf-8")
    # On vérifie qu'on a bien utilisé afficher_echange()
    assert "LIGNE_FORMATTEE" in contenu
    # Et aussi la ligne fallback (avec User: Bonjour)
    assert "User: Bonjour" in contenu


def test_demander_assistant_historique_erreur_mais_pas_de_crash(monkeypatch):
    """
    Couvre le bloc d'exception lors de la récupération de l'historique :
    ConversationDAO.lire_echanges lève une exception → on log un warning
    mais l'appel LLM se fait quand même.
    """
    # On patch LLM_API comme dans ton test précédent
    with patch("src.client.llm_client.LLM_API") as MockLLM:
        mock_client = MockLLM.return_value
        rep = Echange(agent="assistant", message="OK malgré erreur historique", date_msg=Date.today())
        mock_client.generate.return_value = rep

        # Forcer une erreur sur la récupération d'historique
        ConversationDAO.lire_echanges = MagicMock(side_effect=Exception("DB HS"))

        # Forcer un prompt système simple
        monkeypatch.setattr(
            ConversationService,
            "_resoudre_prompt_systeme_pour_conv",
            lambda _id: "PROMPT_SIMPLE",
        )

        e = ConversationService.demander_assistant(
            "Hello",
            options={"temperature": 0.1},
            id_conversation=123,  # → déclenche la tentative de lire_echanges
            id_user=42,
        )

        assert e.agent == "assistant"
        assert "OK malgré erreur" in e.message

        # On vérifie qu'on a quand même appelé le LLM
        mock_client.generate.assert_called_once()