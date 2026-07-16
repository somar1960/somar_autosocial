from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .database import engine, Base
from .routers import auth, content, schedule, analytics
from .services.scheduler import start_scheduler

app = FastAPI(title="SOMAR AutoSocial")

# إنشاء الجداول في قاعدة البيانات
Base.metadata.create_all(bind=engine)

# تضمين الراوترز
app.include_router(auth.router)
app.include_router(content.router)
app.include_router(schedule.router)
app.include_router(analytics.router)

# تشغيل المجدول عند بدء التطبيق
@app.on_event("startup")
def startup():
    start_scheduler()

# نقطة فحص
@app.get("/api/health")
def health():
    return {"status": "ok"}

# خدمة الملفات الثابتة (الواجهة) - يجب أن تكون آخر شيء
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
