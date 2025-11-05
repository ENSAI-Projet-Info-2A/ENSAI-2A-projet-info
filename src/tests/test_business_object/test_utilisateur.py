import re
from unittest.mock import patch

from src.business_object.utilisateur import Utilisateur


# --- Doubles très simples pour les conversations ---
class DummyConv:
    def __init__(self, nom: str):
        self.nom = nom


# ------------------ Affichage / Repr ------------------


def test_afficher_utilisateur_nominal():
    # GIVEN
    u = Utilisateur(pseudo="alice", password_hash="H", id=1)

    # WHEN
    s = u.afficher_utilisateur()

    # THEN
    assert s == "Utilisateur(id=1, pseudo=alice)"


def test_repr_contient_id_et_pseudo():
    # GIVEN
    u = Utilisateur(pseudo="bob", password_hash="H", id=2)

    # WHEN
    r = repr(u)

    # THEN
    assert re.match(r"Utilisateur\(2, 'bob'\)", r)


# ------------------ Egalité (==) ------------------


def test_egalite_par_id_egal():
    # GIVEN
    u1 = Utilisateur(pseudo="x", password_hash="h1", id=42)
    u2 = Utilisateur(pseudo="y", password_hash="h2", id=42)

    # WHEN / THEN
    assert u1 == u2


def test_egalite_par_id_diff():
    # GIVEN
    u1 = Utilisateur(pseudo="x", password_hash="h1", id=1)
    u2 = Utilisateur(pseudo="x", password_hash="h1", id=2)

    # WHEN / THEN
    assert u1 != u2


def test_egalite_objet_autre_type():
    # GIVEN
    u1 = Utilisateur(pseudo="x", password_hash="h1", id=1)

    # WHEN / THEN
    assert u1 != object()


# ------------------ Mot de passe ------------------


def test_set_password_genere_un_hash():
    u = Utilisateur(pseudo="alice", id=10)

    with patch(
        "src.business_object.utilisateur.hash_password", return_value="H(secret|alice)"
    ) as mock_hash:
        u.set_password("secret")

    assert u.password_hash == "H(secret|alice)"
    mock_hash.assert_called_once_with("secret", "alice")


def test_verifier_password_ok():
    u = Utilisateur(pseudo="alice", id=10)

    # 1er appel pour set_password -> "H(secret|alice)"
    # 2e appel pour verifier_password("secret") -> "H(secret|alice)"
    with patch(
        "src.business_object.utilisateur.hash_password",
        side_effect=lambda mdp, sel: f"H({mdp}|{sel})",
    ) as mock_hash:
        u.set_password("secret")
        ok = u.verifier_password("secret")

    assert ok is True
    # 2 appels : set_password et verifier_password
    assert mock_hash.call_count == 2


def test_verifier_password_ko():
    u = Utilisateur(pseudo="alice", id=10)

    with patch(
        "src.business_object.utilisateur.hash_password",
        side_effect=lambda mdp, sel: f"H({mdp}|{sel})",
    ) as mock_hash:
        u.set_password("secret")
        ok = u.verifier_password("mauvais")

    assert ok is False
    # 2 appels : set_password("secret") et verifier_password("mauvais")
    assert mock_hash.call_count == 2


def test_verifier_password_sans_hash_renvoie_false():
    # GIVEN
    u = Utilisateur(pseudo="alice", id=10, password_hash=None)

    # WHEN
    ok = u.verifier_password("peuimporte")

    # THEN
    assert ok is False


def test_from_plain_password_construit_un_user_valide():
    with patch(
        "src.business_object.utilisateur.hash_password",
        side_effect=lambda mdp, sel: f"H({mdp}|{sel})",
    ) as mock_hash:
        u = Utilisateur.from_plain_password("carol", "top")

        assert u.id is None
        assert u.pseudo == "carol"
        assert u.password_hash == "H(top|carol)"
        # vérification avec le même patch (appel 3) :
        assert u.verifier_password("top") is True

    # Appels attendus :
    # 1) set_password("top") dans from_plain_password
    # 2) verifier_password("top") à la fin du test
    assert mock_hash.call_count == 2


# ------------------ Conversations ------------------


def test_ajouter_et_lister_conversations():
    # GIVEN
    u = Utilisateur(pseudo="dave", id=4, password_hash="H")
    c1, c2 = DummyConv("Projet A"), DummyConv("Projet B")

    # WHEN
    u.ajouter_conversation(c1)
    u.ajouter_conversation(c2)

    # THEN
    assert u.lister_conversations() == ["Projet A", "Projet B"]


def test_retirer_conversation():
    # GIVEN
    u = Utilisateur(pseudo="dave", id=4, password_hash="H")
    c1, c2 = DummyConv("Projet A"), DummyConv("Projet B")
    u.ajouter_conversation(c1)
    u.ajouter_conversation(c2)

    # WHEN
    u.retirer_conversation(c1)

    # THEN
    assert u.lister_conversations() == ["Projet B"]


def test_retirer_conversation_absente_est_silencieux():
    # GIVEN
    u = Utilisateur(pseudo="dave", id=4, password_hash="H")
    c1 = DummyConv("Projet A")

    # WHEN (ne lève pas d'exception)
    u.retirer_conversation(c1)

    # THEN
    assert u.lister_conversations() == []
