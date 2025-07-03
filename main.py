import requests
import json
import time
import schedule

# URLs
LOGIN_URL = "https://admin2.khanglobalstudies.com/api/login-with-password"
NEW_LESSONS_URL = "https://admin2.khanglobalstudies.com/api/user/courses/{course_id}/v2-lessons?new=1&medium=1"

# Bot Token & Telegram
BOT_TOKEN = "7541259425:AAFcgg2q7xQ2_xoGP-eRY3G8lcfQbTOoAzM"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Login Credentials
username = "7903443604"
password = "Gautam@123"

# Course Info
COURSES = {
    "696": {"name": "PSIR BY SANJAY THAKUR", "chat_id": "-1002898647258"},
    "686": {"name": "UPSC Mains Answer Writing Program 2025", "chat_id": "-1002565001732"},
    "691": {"name": "UPSC Adhyan Current Affairs (Hindi Medium) Batch 2026", "chat_id": "-1002821163148"},
    "704": {"name": "GEOGRAPHY OPTIONAL HINDI MEDIUM SACHIN ARORA", "chat_id": "-1002871614152"},
    "700": {"name": "HISTORY OPTIONAL HINDI MEDIUM", "chat_id": "-1002662799575"},
    "667": {"name": "UPSC (Pre + Mains) Foundation Batch 2026 Hindi Medium", "chat_id": "-1002810220072"},
    "670": {"name": "UPSC G.S (Prelims+Mains)फाउंडेशन प्रोग्राम 2026 हिंदी माध्यम (Offline Class) Mukherjee Nagar", "chat_id": "-1002642433551"},
    "617": {"name": "Pocket gk batch", "chat_id": "-1002778223155"},
    "372": {"name": "Geography optional english medium", "chat_id": "-1002170644891"}
}

# Headers
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Authorization": "Bearer undefined",
}

def telegram_send_message(text, chat_id):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text[:4096],
        "parse_mode": "HTML"
    }
    try:
        r = requests.post(url, data=payload)
        if r.status_code == 200:
            print(f"[+] Sent to {chat_id}")
        else:
            print(f"[-] Failed to send to {chat_id}: {r.status_code}")
    except Exception as e:
        print(f"[!] Telegram error to {chat_id}: {e}")

def login(username, password):
    payload = {"phone": username, "password": password}
    try:
        print("[*] Logging in...")
        r = requests.post(LOGIN_URL, headers=headers, json=payload)
        if r.status_code == 200:
            token = r.json().get('token')
            if token:
                headers['Authorization'] = f"Bearer {token}"
                print("[+] Login successful")
                return True
        print("[-] Login failed.")
    except Exception as e:
        print(f"[!] Login error: {e}")
    return False

def fetch_and_send(course_id, course_name, chat_id):
    url = NEW_LESSONS_URL.format(course_id=course_id)
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            today_classes = data.get("todayclasses", [])
            if today_classes:
                text = f"<b>📚 {course_name}</b>
<b>🆕 New Lessons:</b>

"
                for cls in today_classes:
                    name = cls.get("name", "No Name")
                    vurl = cls.get("video_url", "No URL")
                    hdurl = cls.get("hd_video_url", "No HD URL")
                    pdfs = cls.get("pdfs") or []
                    text += f"<b>{name}</b>
🔹 {vurl}
🎥 (HD) {hdurl}
"
                    for i, pdf in enumerate(pdfs, 1):
                        pdf_url = pdf.get("url", "No PDF URL")
                        text += f"📄 (PDF {i}) {pdf_url}
"
                    text += "\n"
                telegram_send_message(text, chat_id)
            else:
                print(f"[-] No new lessons for {course_name}")
        else:
            print(f"[-] Failed for {course_name}: {r.status_code}")
    except Exception as e:
        print(f"[!] Error for {course_name}: {e}")

# 🕘 Daily Job
def run_daily_job():
    print("\n🕘 Running scheduled job: Fetch & Send new lessons...\n")
    if login(username, password):
        for course_id, course in COURSES.items():
            fetch_and_send(course_id, course["name"], course["chat_id"])
        print("\n✅ Done: All messages sent.\n")

# ⏰ Schedule at 9:30 PM
schedule.every().day.at("21:30").do(run_daily_job)

print("⏳ Waiting for 9:30 PM daily...")

while True:
    schedule.run_pending()
    time.sleep(30)
