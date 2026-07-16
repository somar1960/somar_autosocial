import openai
from ..config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def generate_caption(prompt_bullets: str, tone="احترافي، جذاب"):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"أنت مساعد تسويقي متخصص في كتابة كابشن إنستغرام بالعربية. اكتب كابشن إبداعيًا وجذابًا بناءً على النقاط التالية. استخدم أسلوب {tone}."},
            {"role": "user", "content": prompt_bullets}
        ],
        temperature=0.8,
        max_tokens=300
    )
    return response.choices[0].message.content.strip()

def generate_reply(comment_text: str):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "أنت مساعد ودود، ترد على تعليقات المتابعين على إنستغرام بردود لطيفة ومختصرة بالعربية. لا تكرر الردود."},
            {"role": "user", "content": comment_text}
        ],
        temperature=0.7,
        max_tokens=60
    )
    return response.choices[0].message.content.strip()

def generate_weekly_report(analytics_data: dict):
    prompt = f"حلل البيانات الأسبوعية التالية لحساب إنستغرام وقدم نصائح لتحسين الأداء: {analytics_data}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "أنت خبير تحليلات إنستغرام. قدم تقريرًا موجزًا ونصائح عملية بالعربية."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=400
    )
    return response.choices[0].message.content.strip()
