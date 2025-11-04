import pytest
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from service.auth_service import Auth_Service, SECRET_KEY


# Classe factice pour simuler la base de données utilisateur
class FakeUtilisateur:
    def __init__(self, id, pseudo, mdp):
        self.id = id
        self.pseudo = pseudo
        self.password_hash = bcrypt.hashpw(mdp.encode(), bcrypt.gensalt()).decode()


class FakeUtilisateurDAO:
    """Simule un DAO avec un seul utilisateur enregistré."""
    def __init__(self):
        self.utilisateur = FakeUtilisateur(1, "alice", "motdepasse123")

    def trouver_par_pseudo(self, pseudo):
        if pseudo == self.utilisateur.pseudo:
            return self.utilisateur
        return None


# FIXTURE pour instancier le service avant chaque test

@pytest.fixture
def auth_service():
    dao = FakeUtilisateurDAO()
    return Auth_Service(dao)


# Test : connexion réussie
def test_se_connecter_succes(auth_service):
    token = auth_service.se_connecter("alice", "motdepasse123")
    assert isinstance(token, str)  # Le token doit être une chaîne
    assert len(token) > 10         # Un token JWT a toujours une certaine longueur
    assert auth_service.verifier_token(token)  # Et il doit être valide


# Test : échec si mauvais mot de passe
def test_se_connecter_mot_de_passe_incorrect(auth_service):
    with pytest.raises(ValueError, match="Mot de passe incorrect."):
        auth_service.se_connecter("alice", "fauxmotdepasse")


# Test : échec si pseudo inexistant
def test_se_connecter_utilisateur_inconnu(auth_service):
    with pytest.raises(ValueError, match="Utilisateur introuvable."):
        auth_service.se_connecter("bob", "motdepasse123")


# Test : déconnexion invalide le token
def test_se_deconnecter(auth_service):
    token = auth_service.se_connecter("alice", "motdepasse123")
    auth_service.se_deconnecter(token)
    assert not auth_service.verifier_token(token)


# Test : token expiré (généré manuellement)
def test_token_expire(auth_service):
    payload = {
        "user_id": 1,
        "pseudo": "alice",
        "exp": datetime.now(timezone.utc) - timedelta(seconds=1),  # déjà expiré  # déjà expiré
    }
    token_expire = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    valid = auth_service.verifier_token(token_expire)
    assert valid is False
