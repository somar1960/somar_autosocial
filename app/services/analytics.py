from ..database import SessionLocal
from ..models import WeeklyAnalytics, PublishedPost
from datetime import datetime, timedelta
from .instagram import get_account_insights, get_media_insights
from .openai_service import generate_weekly_report
import logging

logger = logging.getLogger(__name__)

def fetch_weekly_analytics():
    db = SessionLocal()
    try:
        today = datetime.utcnow()
        start_of_week = today - timedelta(days=today.weekday())
        acc_ins = get_account_insights()
        data = acc_ins.get("data", [])
        followers = 0
        impressions = 0
        reach = 0
        for metric in data:
            if metric["name"] == "follower_count":
                followers = metric["values"][0]["value"]
            elif metric["name"] == "impressions":
                impressions = metric["values"][0]["value"]
            elif metric["name"] == "reach":
                reach = metric["values"][0]["value"]
        week_posts = db.query(PublishedPost).filter(
            PublishedPost.posted_at >= start_of_week
        ).all()
        total_engagement = 0
        for post in week_posts:
            ins = get_media_insights(post.ig_post_id)
            for m in ins.get("data", []):
                if m["name"] == "engagement":
                    total_engagement += m["values"][0]["value"]
        report_text = generate_weekly_report({
            "followers": followers,
            "impressions": impressions,
            "reach": reach,
            "engagement": total_engagement
        })
        wa = WeeklyAnalytics(
            week_start=start_of_week,
            followers=followers,
            impressions=impressions,
            reach=reach,
            engagement=total_engagement,
            report_text=report_text
        )
        db.add(wa)
        db.commit()
        logger.info("Weekly analytics stored.")
    except Exception as e:
        logger.error(f"Analytics error: {e}")
    finally:
        db.close()
