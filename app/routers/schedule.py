from fastapi import APIRouter, Depends
from ..schemas import ScheduleItem
from ..database import SessionLocal
from ..models import ScheduledPost
from ..routers.content import get_current_user
from typing import List

router = APIRouter(prefix="/schedule", tags=["schedule"])

@router.get("/", response_model=List[ScheduleItem])
def get_schedule(user: str = Depends(get_current_user)):
    db = SessionLocal()
    posts = db.query(ScheduledPost).filter(ScheduledPost.posted == False).all()
    db.close()
    return posts
