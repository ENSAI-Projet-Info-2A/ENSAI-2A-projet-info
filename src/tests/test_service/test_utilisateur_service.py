from unittest.mock import MagicMock

from service.utilisateur_service import UtilisateurService
from dao.utilisateur_dao import UtilisateurDao
from business_object.utilisateur import Utilisateur
import service.utilisateur_service as svc  # pour mocker hash_password


# --------- Données factices ----------
liste_utilisateurs = [
    Utilisateur(id=1, pseudo="alice", password_hash="hash1"),
    Utilisateur(id=2, pseudo="bob",   password_hash="hash2"),
    Utilisateur(id=3, pseudo="carol", password_hash="hash3"),
]


# ===================== CREATION =====================

def test_creer_compte_ok():
    """Création d'utilisateur réussie"""

    # GIVEN
    pseudo, mdp = "alice", "1234"
    UtilisateurDao().trouver_par_pseudo = MagicMock(return_value=None)  # pas déjà pris
    UtilisateurDao().creer = MagicMock(return_value=True)
    svc.hash_password = MagicMock(return_value="HASHED")

    # WHEN
    user = UtilisateurService().creer_compte(pseudo, mdp)

    # THEN
    assert user is not None
    assert user.pseudo == pseudo
    assert user.password_hash == "HASHED"
    svc.hash_password.assert_called_once_with(mdp, pseudo)


def test_creer_compte_echec_dao():
    """Création échouée (DAO.creer renvoie False)"""

    # GIVEN
    pseudo, mdp = "bob", "0000"
    UtilisateurDao().trouver_par_pseudo = MagicMock(return_value=None)
    UtilisateurDao().creer = MagicMock(return_value=False)
    svc.hash_password = MagicMock(return_value="HASHED")

    # WHEN
    user = UtilisateurService().creer_compte(pseudo, mdp)

    # THEN
    assert user is None
    svc.hash_password.assert_called_once_with(mdp, pseudo)


def test_creer_compte_pseudo_deja_utilise():
    """Création échouée : pseudo déjà présent en BDD"""

    # GIVEN
    UtilisateurDao().trouver_par_pseudo = MagicMock(return_value=liste_utilisateurs[0])

    # WHEN
    user = UtilisateurService().creer_compte("alice", "secret")

    # THEN
    assert user is None


# ===================== LISTAGE =====================

def test_lister_tous_inclure_hash_true():
    """Lister les utilisateurs en incluant les password_hash"""

    # GIVEN
    UtilisateurDao().lister_tous = MagicMock(return_value=liste_utilisateurs)

    # WHEN
    res = UtilisateurService().lister_tous(inclure_hash=True)

    # THEN
    assert len(res) == 3
    for u in res:
        assert u.password_hash is not None


def test_lister_tous_inclure_hash_false():
    """Lister les utilisateurs en excluant les password_hash"""

    # GIVEN
    UtilisateurDao().lister_tous = MagicMock(
        return_value=[Utilisateur(id=4, pseudo="dave", password_hash="hashX")]
    )

    # WHEN
    res = UtilisateurService().lister_tous()

    # THEN
    assert len(res) == 1
    assert res[0].pseudo == "dave"
    assert res[0].password_hash is None  # masqué par le service


# ===================== RECHERCHE =====================

def test_trouver_par_id():
    """Trouver par id"""

    # GIVEN
    UtilisateurDao().trouver_par_id = MagicMock(return_value=liste_utilisateurs[1])

    # WHEN
    res = UtilisateurService().trouver_par_id(2)

    # THEN
    assert res is not None
    assert res.id == 2
    assert res.pseudo == "bob"


def test_trouver_par_pseudo():
    """Trouver par pseudo"""

    # GIVEN
    UtilisateurDao().trouver_par_pseudo = MagicMock(return_value=liste_utilisateurs[2])

    # WHEN
    res = UtilisateurService().trouver_par_pseudo("carol")

    # THEN
    assert res is not None
    assert res.id == 3
    assert res.pseudo == "carol"


# ===================== PSEUDO DEJA UTILISE =====================

def test_pseudo_deja_utilise_oui():
    """Le pseudo est déjà utilisé"""

    # GIVEN
    UtilisateurDao().trouver_par_pseudo = MagicMock(return_value=liste_utilisateurs[0])

    # WHEN
    res = UtilisateurService().pseudo_deja_utilise("alice")

    # THEN
    assert res is True


def test_pseudo_deja_utilise_non():
    """Le pseudo n'est pas utilisé"""

    # GIVEN
    UtilisateurDao().trouver_par_pseudo = MagicMock(return_value=None)

    # WHEN
    res = UtilisateurService().pseudo_deja_utilise("zozo")

    # THEN
    assert res is False


# ===================== SUPPRESSION =====================

def test_supprimer_succes():
    """Suppression réussie"""

    # GIVEN
    u = Utilisateur(id=5, pseudo="temp", password_hash="h")
    UtilisateurDao().supprimer = MagicMock(return_value=True)

    # WHEN
    ok = UtilisateurService().supprimer(u)

    # THEN
    assert ok is True


def test_supprimer_echec():
    """Suppression échouée"""

    # GIVEN
    u = Utilisateur(id=6, pseudo="temp2", password_hash="h2")
    UtilisateurDao().supprimer = MagicMock(return_value=False)

    # WHEN
    ok = UtilisateurService().supprimer(u)

    # THEN
    assert ok is False


# ===================== CONNEXION =====================

def test_se_connecter_ok():
    """Connexion réussie : pseudo existe et hash concordant"""

    # GIVEN
    user = Utilisateur(id=7, pseudo="eve", password_hash="HASH")
    UtilisateurDao().trouver_par_pseudo = MagicMock(return_value=user)
    svc.hash_password = MagicMock(return_value="HASH")

    # WHEN
    res = UtilisateurService().se_connecter("eve", "secret")

    # THEN
    assert res is not None
    assert res == user
    svc.hash_password.assert_called_once_with("secret", "eve")


def test_se_connecter_mauvais_mdp():
    """Connexion échouée : hash ne correspond pas"""

    # GIVEN
    user = Utilisateur(id=8, pseudo="zoe", password_hash="HASH")
    UtilisateurDao().trouver_par_pseudo = MagicMock(return_value=user)
    svc.hash_password = MagicMock(return_value="AUTREHASH")

    # WHEN
    res = UtilisateurService().se_connecter("zoe", "badpass")

    # THEN
    assert res is None
    svc.hash_password.assert_called_once_with("badpass", "zoe")


def test_se_connecter_pseudo_inconnu():
    """Connexion échouée : pseudo inconnu"""

    # GIVEN
    UtilisateurDao().trouver_par_pseudo = MagicMock(return_value=None)

    # WHEN
    res = UtilisateurService().se_connecter("ghost", "secret")

    # THEN
    assert res is None


# Point d'entrée local
if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
