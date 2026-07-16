from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class LoginRequest(BaseModel):
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UploadResponse(BaseModel):
    image_url: str
    suggested_caption: str
    media_id: Optional[str] = None

class ApprovePost(BaseModel):
    image_url: str
    caption: str
    scheduled_time: Optional[datetime] = None

class ScheduleItem(BaseModel):
    id: int
    image_url: str
    caption: str
    scheduled_time: datetime
    posted: bool

class WeeklyReport(BaseModel):
    week_start: str
    followers: int
    impressions: int
    reach: int
    engagement: int
    report_text: str
