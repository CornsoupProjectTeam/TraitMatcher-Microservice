from jose import jwt, JWTError
from app.config.settings import settings

def verify_and_extract_matching_id(token: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        if payload.get("sub") != "server-to-server":
            return None
        return payload.get("matching_id")
    except JWTError:
        return None
