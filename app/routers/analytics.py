from fastapi import APIRouter, Depends
from ..schemas import WeeklyReport
from ..database import SessionLocal
from ..models import WeeklyAnalytics
from ..routers.content import get_current_user
from ..services.analytics import fetch_weekly_analytics

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.post("/refresh")
def trigger_analytics(user: str = Depends(get_current_user)):
    fetch_weekly_analytics()
    return {"message": "تم تحديث التحليلات الأسبوعية"}

@router.get("/latest", response_model=WeeklyReport)
def latest_report(user: str = Depends(get_current_user)):
    db = SessionLocal()
    report = db.query(WeeklyAnalytics).order_by(WeeklyAnalytics.id.desc()).first()
    db.close()
    if not report:
        return {"detail": "لا توجد تقارير بعد"}
    return {
        "week_start": report.week_start.isoformat(),
        "followers": report.followers,
        "impressions": report.impressions,
        "reach": report.reach,
        "engagement": report.engagement,
        "report_text": report.report_text
    }
