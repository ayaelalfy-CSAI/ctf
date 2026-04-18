import uuid

from sqlalchemy.orm import Session
from models.user import User

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: uuid.UUID):
    return db.query(User).filter_by(id=user_id).first()

def create_user(db: Session, email: str, name: str, google_id: str ,photo: str = None):
    user = User(
        email=email,
        name=name,
        google_id=google_id,
        photo=photo 
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user_photo(db: Session, user_id: uuid.UUID, photo: str):
    user = db.query(User).filter_by(id=user_id).first()
    if user:
        user.photo = photo
        db.commit()
    return user