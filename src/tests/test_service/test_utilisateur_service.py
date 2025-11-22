from unittest.mock import patch

from src.business_object.utilisateur import Utilisateur
from src.service.utilisateur_service import UtilisateurService

# --------- Données factices ----------
liste_utilisateurs = [
    Utilisateur(id=1, pseudo="alice", password_hash="hash1"),
    Utilisateur(id=2, pseudo="bob", password_hash="hash2"),
    Utilisateur(id=3, pseudo="carol", password_hash="hash3"),
]


# ===================== CREATION =====================


def test_normaliser_pseudo_none():
    """_normaliser_pseudo(None) doit renvoyer None."""
    assert UtilisateurService._norm_pseudo(None) is None


def test_normaliser_pseudo_blanc():
    """_normaliser_pseudo avec un pseudo vide ou espaces doit renvoyer None."""
    assert UtilisateurService._norm_pseudo("") is None
    assert UtilisateurService._norm_pseudo("   ") is None


def test_normaliser_pseudo_trim_lower():
    """_normaliser_pseudo doit trimmer et passer en minuscules."""
    res = UtilisateurService._norm_pseudo("  Alice  ")
    assert res == "alice"

def test_creer_compte_ok():
    """Création d'utilisateur réussie"""
    pseudo, mdp = "alice", "1234"
    with (
        patch("src.service.utilisateur_service.UtilisateurDao") as MockDao,
        patch("src.service.utilisateur_service.hash_password", return_value="HASHED") as mock_hash,
    ):
        mock_dao = MockDao.return_value
        mock_dao.trouver_par_pseudo.return_value = None  # pas déjà pris
        mock_dao.creer.return_value = True

        user = UtilisateurService().creer_compte(pseudo, mdp)

        assert user is not None
        assert user.pseudo == pseudo
        assert user.password_hash == "HASHED"
        mock_hash.assert_called_once_with(mdp, pseudo)
        mock_dao.trouver_par_pseudo.assert_called_once_with(pseudo)
        mock_dao.creer_utilisateur.assert_called_once()


def test_creer_compte_echec_dao():
    """Création échouée (DAO.creer_utilisateur renvoie False)"""
    pseudo, mdp = "bob", "0000"
    with (
        patch("src.service.utilisateur_service.UtilisateurDao") as MockDao,
        patch("src.service.utilisateur_service.hash_password", return_value="HASHED") as mock_hash,
    ):
        mock_dao = MockDao.return_value
        mock_dao.trouver_par_pseudo.return_value = None
        mock_dao.creer_utilisateur.return_value = False 

        user = UtilisateurService().creer_compte(pseudo, mdp)

        assert user is None
        mock_hash.assert_called_once_with(mdp, pseudo)
        mock_dao.trouver_par_pseudo.assert_called_once_with(pseudo)
        mock_dao.creer_utilisateur.assert_called_once()

def test_creer_compte_pseudo_vide():
    """Création échouée : pseudo vide → DAO ne doit même pas être appelé."""
    with patch("src.service.utilisateur_service.UtilisateurDao") as MockDao:
        user = UtilisateurService().creer_compte("   ", "mdp")

        assert user is None
        # On vérifie que le DAO n'a pas été utilisé
        MockDao.assert_not_called()

def test_creer_compte_pseudo_deja_utilise():
    """Création échouée : pseudo déjà présent en BDD"""
    with patch("src.service.utilisateur_service.UtilisateurDao") as MockDao:
        mock_dao = MockDao.return_value
        mock_dao.trouver_par_pseudo.return_value = liste_utilisateurs[0]

        user = UtilisateurService().creer_compte("alice", "secret")

        assert user is None
        mock_dao.trouver_par_pseudo.assert_called_once_with("alice")


# ===================== LISTAGE =====================


def test_lister_tous_inclure_hash_true():
    """Lister les utilisateurs en incluant les password_hash"""
    with patch("src.service.utilisateur_service.UtilisateurDao") as MockDao:
        mock_dao = MockDao.return_value
        mock_dao.lister_tous.return_value = liste_utilisateurs

        res = UtilisateurService().lister_tous(inclure_hash=True)

        assert len(res) == 3
        for u in res:
            assert u.password_hash is not None
        mock_dao.lister_tous.assert_called_once()


def test_lister_tous_inclure_hash_false():
    """Lister les utilisateurs en excluant les password_hash"""
    with patch("src.service.utilisateur_service.UtilisateurDao") as MockDao:
        mock_dao = MockDao.return_value
        mock_dao.lister_tous.return_value = [
            Utilisateur(id=4, pseudo="dave", password_hash="hashX")
        ]

        res = UtilisateurService().lister_tous()

        assert len(res) == 1
        assert res[0].pseudo == "dave"
        assert res[0].password_hash is None  # masqué par le service
        mock_dao.lister_tous.assert_called_once()


# ===================== RECHERCHE =====================


def test_trouver_par_id():
    """Trouver par id"""
    with patch("src.service.utilisateur_service.UtilisateurDao") as MockDao:
        mock_dao = MockDao.return_value
        mock_dao.trouver_par_id.return_value = liste_utilisateurs[1]

        res = UtilisateurService().trouver_par_id(2)

        assert res is not None
        assert res.id == 2
        assert res.pseudo == "bob"
        mock_dao.trouver_par_id.assert_called_once_with(2)


def test_trouver_par_pseudo():
    """Trouver par pseudo"""
    with patch("src.service.utilisateur_service.UtilisateurDao") as MockDao:
        mock_dao = MockDao.return_value
        mock_dao.trouver_par_pseudo.return_value = liste_utilisateurs[2]

        res = UtilisateurService().trouver_par_pseudo("carol")

        assert res is not None
        assert res.id == 3
        assert res.pseudo == "carol"
        mock_dao.trouver_par_pseudo.assert_called_once_with("carol")


# ===================== PSEUDO DEJA UTILISE =====================


def test_pseudo_deja_utilise_oui():
    """Le pseudo est déjà utilisé"""
    with patch("src.service.utilisateur_service.UtilisateurDao") as MockDao:
        mock_dao = MockDao.return_value
        mock_dao.trouver_par_pseudo.return_value = liste_utilisateurs[0]

        res = UtilisateurService().pseudo_deja_utilise("alice")

        assert res is True
        mock_dao.trouver_par_pseudo.assert_called_once_with("alice")


def test_pseudo_deja_utilise_non():
    """Le pseudo n'est pas utilisé"""
    with patch("src.service.utilisateur_service.UtilisateurDao") as MockDao:
        mock_dao = MockDao.return_value
        mock_dao.trouver_par_pseudo.return_value = None

        res = UtilisateurService().pseudo_deja_utilise("zozo")

        assert res is False
        mock_dao.trouver_par_pseudo.assert_called_once_with("zozo")


# ===================== SUPPRESSION =====================


def test_supprimer_succes():
    """Suppression réussie"""
    with patch("src.service.utilisateur_service.UtilisateurDao") as MockDao:
        mock_dao = MockDao.return_value
        mock_dao.supprimer.return_value = True
        u = Utilisateur(id=5, pseudo="temp", password_hash="h")

        ok = UtilisateurService().supprimer(u)

        assert ok is True
        mock_dao.supprimer.assert_called_once_with(u)


def test_supprimer_echec():
    """Suppression échouée"""
    with patch("src.service.utilisateur_service.UtilisateurDao") as MockDao:
        mock_dao = MockDao.return_value
        mock_dao.supprimer.return_value = False
        u = Utilisateur(id=6, pseudo="temp2", password_hash="h2")

        ok = UtilisateurService().supprimer(u)

        assert ok is False
        mock_dao.supprimer.assert_called_once_with(u)


# ===================== CONNEXION =====================


def test_se_connecter_ok():
    """Connexion réussie : pseudo existe et hash concordant"""
    user = Utilisateur(id=7, pseudo="eve", password_hash="HASH")
    with (
        patch("src.service.utilisateur_service.UtilisateurDao") as MockDao,
        patch("src.business_object.utilisateur.hash_password", return_value="HASH") as mock_hash,
    ):
        mock_dao = MockDao.return_value
        mock_dao.trouver_par_pseudo.return_value = user

        res = UtilisateurService().se_connecter("eve", "secret")

        assert res is not None
        assert res == user
        mock_hash.assert_called_once_with("secret", "eve")
        mock_dao.trouver_par_pseudo.assert_called_once_with("eve")


def test_se_connecter_mauvais_mdp():
    """Connexion échouée : hash ne correspond pas"""
    user = Utilisateur(id=8, pseudo="zoe", password_hash="HASH")
    with (
        patch("src.service.utilisateur_service.UtilisateurDao") as MockDao,
        patch(
            "src.business_object.utilisateur.hash_password", return_value="AUTREHASH"
        ) as mock_hash,
    ):
        mock_dao = MockDao.return_value
        mock_dao.trouver_par_pseudo.return_value = user

        res = UtilisateurService().se_connecter("zoe", "badpass")

        assert res is None
        mock_hash.assert_called_once_with("badpass", "zoe")
        mock_dao.trouver_par_pseudo.assert_called_once_with("zoe")


def test_se_connecter_pseudo_inconnu():
    """Connexion échouée : pseudo inconnu"""
    with patch("src.service.utilisateur_service.UtilisateurDao") as MockDao:
        mock_dao = MockDao.return_value
        mock_dao.trouver_par_pseudo.return_value = None

        res = UtilisateurService().se_connecter("ghost", "secret")

        assert res is None
        mock_dao.trouver_par_pseudo.assert_called_once_with("ghost")

def test_se_connecter_pseudo_vide():
    """Connexion échouée : pseudo vide → DAO ne doit pas être appelé."""
    with patch("src.service.utilisateur_service.UtilisateurDao") as MockDao:
        res = UtilisateurService().se_connecter("   ", "secret")

        assert res is None
        MockDao.assert_not_called()
        
# Point d'entrée local
if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
