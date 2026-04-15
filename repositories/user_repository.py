from sqlalchemy.orm import Session
from models.user import User

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, email: str, name: str, google_id: str):
    user = User(
        email=email,
        name=name,
        google_id=google_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user