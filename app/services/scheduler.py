from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from ..database import SessionLocal
from ..models import ScheduledPost, PublishedPost, CommentReply
from .instagram import create_media_container, publish_container, get_recent_comments, reply_to_comment
from .openai_service import generate_reply
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def check_and_publish():
    """نشر المنشورات المجدولة التي حان وقتها"""
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        posts = db.query(ScheduledPost).filter(
            ScheduledPost.scheduled_time <= now,
            ScheduledPost.posted == False
        ).all()
        for post in posts:
            container = create_media_container(post.image_url, post.caption)
            if "id" in container:
                creation_id = container["id"]
                publish_res = publish_container(creation_id)
                if "id" in publish_res:
                    post.posted = True
                    post.creation_id = creation_id
                    db.add(post)
                    pub = PublishedPost(
                        ig_post_id=publish_res["id"],
                        caption=post.caption,
                        image_url=post.image_url
                    )
                    db.add(pub)
                    db.commit()
                    logger.info(f"Published scheduled post {post.id}")
                else:
                    logger.error(f"Publish failed for {post.id}: {publish_res}")
            else:
                logger.error(f"Container creation failed for {post.id}: {container}")
    except Exception as e:
        logger.error(f"Error in check_and_publish: {e}")
    finally:
        db.close()

def auto_reply_comments():
    """الرد التلقائي على التعليقات الجديدة"""
    db = SessionLocal()
    try:
        comments = get_recent_comments()
        for c in comments:
            exists = db.query(CommentReply).filter(
                CommentReply.ig_comment_id == c["comment_id"]
            ).first()
            if not exists:
                reply_text = generate_reply(c["text"])
                res = reply_to_comment(c["comment_id"], reply_text)
                if "id" in res:
                    cr = CommentReply(
                        ig_comment_id=c["comment_id"],
                        ig_media_id=c["media_id"],
                        reply_text=reply_text
                    )
                    db.add(cr)
                    db.commit()
                    logger.info(f"Replied to comment {c['comment_id']}")
    except Exception as e:
        logger.error(f"Error in auto_reply: {e}")
    finally:
        db.close()

def start_scheduler():
    scheduler.add_job(check_and_publish, 'interval', minutes=1)
    scheduler.add_job(auto_reply_comments, 'interval', minutes=30)
    scheduler.start()
