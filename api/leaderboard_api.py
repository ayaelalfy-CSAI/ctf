from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from core.deps import get_current_user
from models.user import User
from models.user_progress import UserProgress
from models.character import Character

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])

@router.get("/me")
def get_my_rank(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    users = db.query(User).filter(User.role == "user").order_by(User.points.desc()).all()

  
    rank = next((i + 1 for i, u in enumerate(users) if u.id == current_user.id), None)

   
    last_progress = db.query(UserProgress).filter_by(
        user_id=current_user.id,
        completed=True
    ).order_by(UserProgress.completed_at.desc()).first()

    last_completed_level = None
    if last_progress:
        character = db.query(Character).filter_by(
            id=last_progress.character_id
        ).first()
        if character:
            last_completed_level = character.level

    total_characters = db.query(Character).count()        

    return {
        "rank": rank,
        "points": current_user.points,
        "name": current_user.name,
        "last_completed_level": last_completed_level or 0,
        "total_characters": total_characters
    }

@router.get("/")
def get_leaderboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    users = db.query(User).order_by(User.points.desc()).all()
    result = []
    for rank, user in enumerate(users, start=1):
        result.append({
            "rank": rank,
            "name": user.name,
            "points": user.points,
            "is_me": user.id == current_user.id
        })
    return result