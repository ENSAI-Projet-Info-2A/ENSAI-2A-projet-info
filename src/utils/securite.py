import hashlib
import bcrypt


def hash_password(password, sel=""):
    """Hachage du mot de passe"""
    password_bytes = password.encode("utf-8") + sel.encode("utf-8")
    hash_object = hashlib.sha256(password_bytes)
    return hash_object.hexdigest()

def verifier_mot_de_passe(mot_de_passe_clair: str, hash_stocke: str) -> bool:
    return bcrypt.checkpw(mot_de_passe_clair.encode(), hash_stocke.encode())
