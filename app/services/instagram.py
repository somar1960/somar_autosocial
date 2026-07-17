import requests
import os
from ..config import PAGE_ACCESS_TOKEN, INSTAGRAM_BUSINESS_ACCOUNT_ID

BASE_URL = "https://graph.facebook.com/v19.0"
TEMP_DIR = "temp_images"

# تأكد من وجود المجلد المؤقت
os.makedirs(TEMP_DIR, exist_ok=True)

def save_temp_image(file_bytes: bytes, filename: str, base_url: str) -> str:
    """حفظ الصورة مؤقتاً وإرجاع رابطها العام"""
    filepath = os.path.join(TEMP_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(file_bytes)
    return f"{base_url}/temp/{filename}"

def delete_temp_image(filename: str):
    filepath = os.path.join(TEMP_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)

def create_media_container(image_url: str, caption: str):
    """إنشاء حاوية وسائط (صورة)"""
    url = f"{BASE_URL}/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media"
    params = {
        "image_url": image_url,
        "caption": caption,
        "access_token": PAGE_ACCESS_TOKEN
    }
    r = requests.post(url, params=params)
    return r.json()

def publish_container(creation_id: str):
    """نشر الحاوية"""
    url = f"{BASE_URL}/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media_publish"
    params = {
        "creation_id": creation_id,
        "access_token": PAGE_ACCESS_TOKEN
    }
    r = requests.post(url, params=params)
    return r.json()

def get_media_insights(media_id: str):
    url = f"{BASE_URL}/{media_id}/insights"
    params = {"metric": "engagement,impressions,reach", "access_token": PAGE_ACCESS_TOKEN}
    r = requests.get(url, params=params)
    return r.json()

def get_account_insights():
    url = f"{BASE_URL}/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/insights"
    params = {
        "metric": "follower_count,impressions,reach,profile_views",
        "period": "day",
        "access_token": PAGE_ACCESS_TOKEN
    }
    r = requests.get(url, params=params)
    return r.json()

def get_recent_comments():
    """جلب أحدث وسائط المنشورات وجلب التعليقات غير المردود عليها"""
    url = f"{BASE_URL}/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media"
    params = {"fields": "id,comments{id,text,timestamp}", "access_token": PAGE_ACCESS_TOKEN, "limit": 10}
    r = requests.get(url, params=params)
    media_list = r.json().get("data", [])
    comments_to_reply = []
    for media in media_list:
        media_id = media["id"]
        comments = media.get("comments", {}).get("data", [])
        for comment in comments:
            comments_to_reply.append({
                "media_id": media_id,
                "comment_id": comment["id"],
                "text": comment["text"]
            })
    return comments_to_reply

def reply_to_comment(comment_id: str, message: str):
    url = f"{BASE_URL}/{comment_id}/replies"
    params = {
        "message": message,
        "access_token": PAGE_ACCESS_TOKEN
    }
    r = requests.post(url, params=params)
    return r.json()
