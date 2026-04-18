from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from core.deps import get_current_user
from models.user import User

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])

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
        })
    return result