from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, default="admin")
    hashed_password = Column(String)

class ScheduledPost(Base):
    __tablename__ = "scheduled_posts"
    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(Text, nullable=True)
    media_type = Column(String)
    caption = Column(Text)
    scheduled_time = Column(DateTime(timezone=True))
    posted = Column(Boolean, default=False)
    creation_id = Column(String, nullable=True)

class PublishedPost(Base):
    __tablename__ = "published_posts"
    id = Column(Integer, primary_key=True, index=True)
    ig_post_id = Column(String)
    caption = Column(Text)
    image_url = Column(Text)
    posted_at = Column(DateTime(timezone=True), server_default=func.now())

class CommentReply(Base):
    __tablename__ = "comment_replies"
    id = Column(Integer, primary_key=True, index=True)
    ig_comment_id = Column(String, unique=True)
    ig_media_id = Column(String)
    reply_text = Column(Text)
    replied_at = Column(DateTime(timezone=True), server_default=func.now())

class WeeklyAnalytics(Base):
    __tablename__ = "weekly_analytics"
    id = Column(Integer, primary_key=True, index=True)
    week_start = Column(DateTime(timezone=True))
    followers = Column(Integer)
    impressions = Column(Integer)
    reach = Column(Integer)
    engagement = Column(Integer)
    report_text = Column(Text)
