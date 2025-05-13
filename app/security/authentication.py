from jose import jwt, JWTError
from app.config.settings import settings
from typing import Optional

def verify_and_extract_matching_id(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        if payload.get("sub") != "server-to-server":
            return None
        return payload.get("matching_id")
    except JWTError:
        return None
