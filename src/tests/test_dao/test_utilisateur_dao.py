import os
from unittest.mock import MagicMock, patch

import pytest

from src.business_object.utilisateur import Utilisateur
from src.dao.utilisateur_dao import UtilisateurDao
from src.utils.reset_database import ResetDatabase


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialisation des données de test"""
    with patch.dict(os.environ, {"SCHEMA": "projet_test_dao"}):
        ResetDatabase().lancer(test_dao=True)
        yield


def test_trouver_par_id_existant():
    """Recherche par id d'un utilisateur existant"""
    # GIVEN
    id = 1
    # WHEN
    utilisateur = UtilisateurDao().trouver_par_id(id)
    # THEN
    assert utilisateur is not None
    # assert isinstance(utilisateur, Utilisateur)
    assert utilisateur.pseudo == "user_alpha"


def test_trouver_par_id_non_existant():
    """Recherche par id d'un utilisateur n'existant pas"""
    # GIVEN
    id = 9999999999999
    # WHEN
    utilisateur = UtilisateurDao().trouver_par_id(id)
    # THEN
    assert utilisateur is None


def test_trouver_par_pseudo_existant():
    """Recherche par pseudo d'un utilisateur existant"""
    # GIVEN
    pseudo = "user_bravo"
    # WHEN
    utilisateur = UtilisateurDao().trouver_par_pseudo(pseudo)
    # THEN
    assert utilisateur is not None
    # assert isinstance(utilisateur, Utilisateur)
    assert utilisateur.pseudo == pseudo
    assert utilisateur.id == 2


def test_trouver_par_pseudo_exception_sql():
    """simulateur d'erreur SQL via mock sur cursor.execute"""

    faux_cursor = MagicMock()
    faux_cursor.execute.side_effect = Exception("SQL ERROR")

    faux_conn = MagicMock()
    faux_conn.cursor.return_value.__enter__.return_value = faux_cursor

    with patch("src.dao.utilisateur_dao.DBConnection") as MockDB:
        MockDB.return_value.connection.__enter__.return_value = faux_conn

        with pytest.raises(Exception):
            UtilisateurDao().trouver_par_pseudo("abc")


def test_trouver_par_pseudo_non_existant():
    """Recherche par pseudo d'un utilisateur n'existant pas"""
    # GIVEN
    pseudo = "utilisateur_inexistant_xyz"
    # WHEN
    utilisateur = UtilisateurDao().trouver_par_pseudo(pseudo)
    # THEN
    assert utilisateur is None


def test_creer_utilisateur_ok():
    """Création d'utilisateur réussie"""
    # GIVEN
    utilisateur = Utilisateur(pseudo="nouveau_user_test", password_hash="password123")
    # WHEN
    creation_ok = UtilisateurDao().creer_utilisateur(utilisateur)
    # THEN
    assert creation_ok
    assert utilisateur is not None


def test_creer_utilisateur_ko():
    """Création d'utilisateur échouée (pseudo déjà existant)"""
    # GIVEN
    utilisateur = Utilisateur(pseudo="user_alpha", password_hash="password")
    # WHEN
    creation_ok = UtilisateurDao().creer_utilisateur(utilisateur)
    # THEN
    assert not creation_ok


def test_lister_tous_exception_sql():
    faux_cursor = MagicMock()
    faux_cursor.execute.side_effect = Exception("FAIL SELECT")

    faux_conn = MagicMock()
    faux_conn.cursor.return_value.__enter__.return_value = faux_cursor

    with patch("src.dao.utilisateur_dao.DBConnection") as MockDB:
        MockDB.return_value.connection.__enter__.return_value = faux_conn

        with pytest.raises(Exception):
            UtilisateurDao().lister_tous()


def test_supprimer_ok():
    """Suppression d'utilisateur réussie"""
    # GIVEN
    utilisateur = Utilisateur(id=10, pseudo="juliet42")
    # WHEN
    suppression_ok = UtilisateurDao().supprimer(utilisateur)
    # THEN
    assert suppression_ok
    # Vérification que l'utilisateur n'existe plus
    utilisateur_supprime = UtilisateurDao().trouver_par_id(10)
    assert utilisateur_supprime is None


def test_supprimer_ko():
    """Suppression d'utilisateur échouée (id inconnu)"""
    # GIVEN
    utilisateur = Utilisateur(id=8888888, pseudo="id_inconnu")
    # WHEN
    suppression_ok = UtilisateurDao().supprimer(utilisateur)
    # THEN
    assert not suppression_ok


def test_supprimer_exception_sql():
    utilisateur = Utilisateur(id=1, pseudo="x")

    faux_cursor = MagicMock()
    faux_cursor.execute.side_effect = Exception("DELETE FAIL")

    faux_conn = MagicMock()
    faux_conn.cursor.return_value.__enter__.return_value = faux_cursor

    with patch("src.dao.utilisateur_dao.DBConnection") as MockDB:
        MockDB.return_value.connection.__enter__.return_value = faux_conn

        with pytest.raises(Exception):
            UtilisateurDao().supprimer(utilisateur)


def test_heures_utilisation_avec_sessions():
    """Calcul des heures d'utilisation pour un utilisateur avec des sessions"""
    # GIVEN
    id_utilisateur = 1
    # WHEN
    heures = UtilisateurDao().heures_utilisation(id_utilisateur)
    # THEN
    assert isinstance(heures, float)
    assert heures >= 0.0


def test_heures_utilisation_sans_sessions():
    """Calcul des heures d'utilisation pour un utilisateur sans sessions"""
    # GIVEN
    id_utilisateur = 9999999
    # WHEN
    heures = UtilisateurDao().heures_utilisation(id_utilisateur)
    # THEN
    assert heures == 0.0


def test_heures_utilisation_exception_sql():
    faux_cursor = MagicMock()
    faux_cursor.execute.side_effect = Exception("BAD QUERY")

    faux_conn = MagicMock()
    faux_conn.cursor.return_value.__enter__.return_value = faux_cursor

    with patch("src.dao.utilisateur_dao.DBConnection") as MockDB:
        MockDB.return_value.connection.__enter__.return_value = faux_conn

        with pytest.raises(Exception):
            UtilisateurDao().heures_utilisation(99)


def test_heures_utilisation_incl_courante_ok():
    heures = UtilisateurDao().heures_utilisation_incl_courante(1)
    assert isinstance(heures, float)
    assert heures >= 0.0


def test_heures_utilisation_incl_courante_exception_sql():
    faux_cursor = MagicMock()
    faux_cursor.execute.side_effect = Exception("NOW() FAIL")

    faux_conn = MagicMock()
    faux_conn.cursor.return_value.__enter__.return_value = faux_cursor

    with patch("src.dao.utilisateur_dao.DBConnection") as MockDB:
        MockDB.return_value.connection.__enter__.return_value = faux_conn

        with pytest.raises(Exception):
            UtilisateurDao().heures_utilisation_incl_courante(1)


if __name__ == "__main__":
    pytest.main([__file__])
