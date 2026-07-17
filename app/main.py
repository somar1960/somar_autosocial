from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from .database import engine, Base
from .routers import auth, content, schedule, analytics
from .services.scheduler import start_scheduler

app = FastAPI(title="SOMAR AutoSocial")

# إنشاء الجداول
Base.metadata.create_all(bind=engine)

# تضمين الراوترز
app.include_router(auth.router)
app.include_router(content.router)
app.include_router(schedule.router)
app.include_router(analytics.router)

# تشغيل المجدول
@app.on_event("startup")
def startup():
    start_scheduler()

# نقطة فحص
@app.get("/api/health")
def health():
    return {"status": "ok"}

# مجلد الصور المؤقتة
os.makedirs("temp_images", exist_ok=True)
app.mount("/temp", StaticFiles(directory="temp_images"), name="temp")

# صفحة البداية (الواجهة)
@app.get("/")
def read_index():
    return FileResponse("app/static/index.html")

# خدمة باقي الملفات الثابتة (CSS, JS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
