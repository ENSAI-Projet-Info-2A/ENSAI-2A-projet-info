import jwt 
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

def creer_token(user_id: int, pseudo: str, duree_heures: int = 1) -> str:
    payload = {
        "user_id": user_id,
        "pseudo": pseudo,
        "exp": datetime.now(timezone.utc) + timedelta(hours=duree_heures),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    
def verifier_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
