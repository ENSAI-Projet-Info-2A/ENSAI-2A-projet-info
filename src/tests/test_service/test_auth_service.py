import pytest
from unittest.mock import MagicMock
from src.dao.utilisateur_dao import UtilisateurDao
from src.business_object.utilisateur import Utilisateur
from src.service.auth_service import Auth_Service


class TestAuthService:
    def test_se_connecter_succes(self):
        # GIVEN
        mock_utilisateur_dao = MagicMock(spec=UtilisateurDao)
        mock_utilisateur = MagicMock(spec=Utilisateur)
        mock_utilisateur.id = 1
        mock_utilisateur.pseudo = "alice"
        mock_utilisateur.verifier_password.return_value = True
        mock_utilisateur_dao.trouver_par_pseudo.return_value = mock_utilisateur

        # WHEN
        auth_service = Auth_Service(mock_utilisateur_dao)
        token = auth_service.se_connecter("alice", "motdepasse123")

        # THEN
        assert token is not None  
        assert isinstance(token, str) 
        assert len(token) > 0 
        mock_utilisateur_dao.trouver_par_pseudo.assert_called_once_with("alice")
        mock_utilisateur.verifier_password.assert_called_once_with("motdepasse123")

    def test_se_connecter_utilisateur_introuvable(self):
        # GIVEN
        mock_utilisateur_dao = MagicMock(spec=UtilisateurDao)
        mock_utilisateur_dao.trouver_par_pseudo.return_value = None

        # WHEN
        auth_service = Auth_Service(mock_utilisateur_dao)

        # THEN
        with pytest.raises(ValueError, match="Utilisateur introuvable."):
            auth_service.se_connecter("alice", "motdepasse123")

    def test_se_connecter_mot_de_passe_incorrect(self):
        # GIVEN
        mock_utilisateur_dao = MagicMock(spec=UtilisateurDao)
        mock_utilisateur = MagicMock(spec=Utilisateur)
        mock_utilisateur.verifier_password.return_value = False
        mock_utilisateur_dao.trouver_par_pseudo.return_value = mock_utilisateur

        # WHEN
        auth_service = Auth_Service(mock_utilisateur_dao)

        # THEN
        with pytest.raises(ValueError, match="Mot de passe incorrect."):
            auth_service.se_connecter("alice", "motdepasse123")

    def test_se_deconnecter(self):
        # GIVEN
        mock_utilisateur_dao = MagicMock(spec=UtilisateurDao)
        auth_service = Auth_Service(mock_utilisateur_dao)
        
        # WHEN
        auth_service.se_deconnecter("token123")
        
        # THEN
        assert "token123" in auth_service.tokens_invalides

    def test_verifier_token_valide(self):
        # GIVEN
        mock_utilisateur_dao = MagicMock(spec=UtilisateurDao)
        auth_service = Auth_Service(mock_utilisateur_dao)
        
        # 
        mock_utilisateur = MagicMock(spec=Utilisateur)
        mock_utilisateur.id = 1
        mock_utilisateur.pseudo = "alice"
        mock_utilisateur.verifier_password.return_value = True
        mock_utilisateur_dao.trouver_par_pseudo.return_value = mock_utilisateur
        
        token = auth_service.se_connecter("alice", "motdepasse123")
        
        # WHEN
        result = auth_service.verifier_token(token)
        
        # THEN
        assert result is True

    def test_verifier_token_invalide(self):
        # GIVEN
        mock_utilisateur_dao = MagicMock(spec=UtilisateurDao)
        auth_service = Auth_Service(mock_utilisateur_dao)
        
        # WHEN 
        result = auth_service.verifier_token("token_completement_invalide")
        
        # THEN
        assert result is False

    def test_verifier_token_invalide_dans_liste_noire(self):
        # GIVEN
        mock_utilisateur_dao = MagicMock(spec=UtilisateurDao)
        auth_service = Auth_Service(mock_utilisateur_dao)
        
        # 
        mock_utilisateur = MagicMock(spec=Utilisateur)
        mock_utilisateur.id = 1
        mock_utilisateur.pseudo = "alice"
        mock_utilisateur.verifier_password.return_value = True
        mock_utilisateur_dao.trouver_par_pseudo.return_value = mock_utilisateur
        
        token = auth_service.se_connecter("alice", "motdepasse123")
        auth_service.tokens_invalides.add(token)
        
        # WHEN
        result = auth_service.verifier_token(token)
        
        # THEN
        assert result is False