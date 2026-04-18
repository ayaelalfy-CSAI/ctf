from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.auth_schema import GoogleAuthRequest, TokenResponse
from services.auth_service import exchange_code_for_token, get_user_info
from services.jwt_service import create_access_token
from repositories.user_repository import get_user_by_email, create_user


router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/google/login", response_model=TokenResponse)
def google_login(request: GoogleAuthRequest, db: Session = Depends(get_db)):
    
    # 1. exchange code → token
    token_data = exchange_code_for_token(request.code)

    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Failed to exchange code for token")

    #  2. get user info
    user_info = get_user_info(access_token)

    email = user_info["email"]
    if "email" not in user_info:
      raise HTTPException(status_code=400, detail="Invalid Google response")


    name = user_info.get("name")
    google_id = user_info["id"]
    photo = user_info.get("picture")

    # 3. check user
    user = get_user_by_email(db, email)
    if not user:
        user = create_user(db, email, name, google_id, photo)  
    else:
        # ← لو موجود حدّث الـ photo لو اتغيرت
        user.photo = photo
        db.commit()
        db.refresh(user)


    #  4. create JWT
    jwt_token = create_access_token({
        "user_id": str(user.id),
        "role": user.role,
        "name": user.name,
        "photo": user.photo 
    })

    return {
        "access_token": jwt_token,
        "token_type": "bearer"
    }