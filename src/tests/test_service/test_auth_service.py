import pytest
from src.dao.utilisateur_dao import UtilisateurDao
from src.business_object.utilisateur import Utilisateur
from src.service.auth_service import Auth_Service
from dotenv import load_dotenv

load_dotenv('.env')


class TestAuthService:
    @pytest.fixture(scope="function")
    def auth_service(self):
        """Fixture qui initialise le service avec le DAO de test"""
        dao = UtilisateurDao()
        return Auth_Service(dao)
    
    @pytest.fixture(scope="function")
    def utilisateur_test(self):
        """Fixture qui crée un utilisateur de test dans la DB"""
        dao = UtilisateurDao()
        utilisateur = Utilisateur.from_plain_password(
            pseudo="alice_test",
            mot_de_passe="Password123!"  
        )
        dao.creer_utilisateur(utilisateur)
        yield utilisateur
        # Nettoyage
        dao.supprimer(utilisateur)

    def test_se_connecter_succes(self, auth_service, utilisateur_test):
        # WHEN
        token = auth_service.se_connecter("alice_test", "Password123!")

        # THEN
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_se_connecter_utilisateur_introuvable(self, auth_service):
        # THEN
        with pytest.raises(ValueError, match="Utilisateur introuvable."):
            auth_service.se_connecter("utilisateur_inexistant", "motdepasse")

    def test_se_connecter_mot_de_passe_incorrect(self, auth_service, utilisateur_test):
        # THEN
        with pytest.raises(ValueError, match="Mot de passe incorrect."):
            auth_service.se_connecter("alice_test", "mauvais_password")

    def test_se_deconnecter(self, auth_service, utilisateur_test):
        # GIVEN - Créer un vrai token
        token = auth_service.se_connecter("alice_test", "Password123!")
        
        # WHEN
        auth_service.se_deconnecter(token)
        
        # THEN
        assert token in auth_service.tokens_invalides

    def test_verifier_token_valide(self, auth_service, utilisateur_test):
        # GIVEN
        token = auth_service.se_connecter("alice_test", "Password123!")
        
        # WHEN
        result = auth_service.verifier_token(token)
        
        # THEN
        assert result is True

    def test_verifier_token_invalide(self, auth_service):
        # WHEN
        result = auth_service.verifier_token("token_completement_invalide")
        
        # THEN
        assert result is False

    def test_verifier_token_invalide_dans_liste_noire(self, auth_service, utilisateur_test):
        # GIVEN
        token = auth_service.se_connecter("alice_test", "Password123!")
        auth_service.se_deconnecter(token)
        
        # WHEN
        result = auth_service.verifier_token(token)
        
        # THEN
        assert result is False