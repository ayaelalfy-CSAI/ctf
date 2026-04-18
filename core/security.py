from jose import jwt, JWTError
from core.config import settings
import logging as py_logging

logger = py_logging.getLogger(__name__)

ALGORITHM = "HS256"

def decode_jwt(token: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        logger.warning(f"PAYLOAD: {payload}")
        return payload.get("user_id")
    except JWTError as e:
        logger.warning(f"JWT ERROR: {e}")
        return None