from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import decode_jwt
from models.user import User
import logging as py_logging

logger = py_logging.getLogger(__name__)  # ← استخدم py_logging

bearer = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials

    logger.warning(f"TOKEN RECEIVED: {token[:50]}...")
    user_id = decode_jwt(token)
    logger.warning(f"USER ID DECODED: {user_id}")
    


    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

def get_admin_user(  # ← ضيف الدالة دي
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins only!"
        )
    return current_user