from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..schemas import UploadResponse, ApprovePost
from ..services.instagram import save_temp_image, create_media_container, publish_container
from ..services.openai_service import generate_caption
from ..database import SessionLocal
from ..models import ScheduledPost, PublishedPost
from jose import jwt, JWTError
from ..config import SECRET_KEY, ALGORITHM, BASE_URL
from datetime import datetime
import uuid

router = APIRouter(prefix="/content", tags=["content"])
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="توكن غير صالح")

@router.post("/upload", response_model=UploadResponse)
async def upload_media(
    file: UploadFile = File(...),
    bullets: str = Form(""),
    user: str = Depends(get_current_user)
):
    contents = await file.read()
    ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    unique_name = f"{uuid.uuid4()}.{ext}"
    image_url = save_temp_image(contents, unique_name, BASE_URL)
    caption = ""
    if bullets.strip():
        caption = generate_caption(bullets)
    return UploadResponse(image_url=image_url, suggested_caption=caption)

@router.post("/approve")
def approve_and_post(
    data: ApprovePost,
    user: str = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        if data.scheduled_time is None:
            container = create_media_container(data.image_url, data.caption)
            if "id" not in container:
                raise HTTPException(status_code=400, detail=f"Container creation failed: {container}")
            creation_id = container["id"]
            pub = publish_container(creation_id)
            if "id" not in pub:
                raise HTTPException(status_code=400, detail=f"Publish failed: {pub}")
            published = PublishedPost(
                ig_post_id=pub["id"],
                caption=data.caption,
                image_url=data.image_url
            )
            db.add(published)
            db.commit()
            return {"message": "تم النشر بنجاح", "post_id": pub["id"]}
        else:
            scheduled = ScheduledPost(
                image_url=data.image_url,
                caption=data.caption,
                scheduled_time=data.scheduled_time,
                media_type="IMAGE"
            )
            db.add(scheduled)
            db.commit()
            return {"message": "تمت الجدولة بنجاح", "scheduled_id": scheduled.id}
    finally:
        db.close()
