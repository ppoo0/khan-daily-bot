import requests
from datetime import datetime
import schedule
import time

# Telegram Bot Config
BOT_TOKEN = "7541259425:AAFcgg2q7xQ2_xoGP-eRY3G8lcfQbTOoAzM"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Courses
COURSES = {
    "696": {"name": "PSIR BY SANJAY THAKUR", "chat_id": "-1002898647258"},
    "686": {"name": "UPSC Mains Answer Writing Program 2025", "chat_id": "-1002565001732"},
    "691": {"name": "UPSC Adhyan Current Affairs (Hindi Medium) Batch 2026", "chat_id": "-1002821163148"},
    "704": {"name": "GEOGRAPHY OPTIONAL HINDI MEDIUM SACHIN ARORA", "chat_id": "-1002871614152"},
    "700": {"name": "HISTORY OPTIONAL HINDI MEDIUM", "chat_id": "-1002662799575"},
    "667": {"name": "UPSC (Pre + Mains) Foundation Batch 2026 Hindi Medium", "chat_id": "-1002810220072"},
    "670": {"name": "UPSC G.S (Prelims+Mains)फाउंडेशन प्रोग्राम 2026 हिंदी माध्यम (Offline Class) Mukherjee Nagar", "chat_id": "-1002642433551"},
    "617": {"name": "Pocket gk batch","chat_id": "-1002778223155"},
    "372": {"name": "Geography optional english medium","chat_id": "-1002170644891"}
}

LOGIN_URL = "https://admin2.khanglobalstudies.com/api/login-with-password"
LESSONS_URL = "https://admin2.khanglobalstudies.com/api/user/courses/{course_id}/v2-lessons?new=1&medium=1"

username = "7903443604"
password = "Gautam@123"

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Authorization": "Bearer undefined"
}

def telegram_send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text[:4096], "parse_mode": "HTML"}
    try:
        r = requests.post(url, data=payload)
        if r.status_code == 200:
            print(f"[+] Sent to {chat_id}")
        else:
            print(f"[-] Failed for {chat_id}: {r.status_code}")
    except Exception as e:
        print(f"[!] Telegram error: {e}")

def login():
    payload = {"phone": username, "password": password}
    try:
        print("[*] Logging in...")
        r = requests.post(LOGIN_URL, headers=headers, json=payload)
        if r.status_code == 200:
            token = r.json().get("token")
            if token:
                headers['Authorization'] = f"Bearer {token}"
                print("[+] Login successful")
                return True
        print("[-] Login failed")
    except Exception as e:
        print(f"[!] Login error: {e}")
    return False

def fetch_all_courses():
    for course_id, course_info in COURSES.items():
        url = LESSONS_URL.format(course_id=course_id)
        try:
            r = requests.get(url, headers=headers)
            if r.status_code != 200:
                print(f"[!] Failed to fetch for {course_info['name']}")
                continue

            data = r.json()
            today_classes = data.get("todayclasses", [])
            if not today_classes:
                print(f"[-] No new lessons for {course_info['name']}")
                continue

            for cls in today_classes:
                name = cls.get("name", "No Name")
                video_url = cls.get("video_url")
                hd_url = cls.get("hd_video_url")
                pdfs = cls.get("pdfs", [])

                notes_links = ""
                ppt_links = ""

                for pdf in pdfs:
                    title = pdf.get("title", "").lower()
                    url = pdf.get("url", "")
                    if "ppt" in title:
                        ppt_links += f"📄 <a href=\"{url}\">PPT</a>\n"
                    else:
                        notes_links += f"📝 <a href=\"{url}\">Notes</a>\n"

                message = (
                    f"𝗧𝗛𝗜𝗦 𝗠𝗘𝗦𝗦𝗔𝗚𝗘 𝗦𝗘𝗡𝗧 𝗕𝗬 💞𝙼𝚁 𝚁𝙰𝙹𝙿𝚄𝚃💞\n"
                    f"📅 Date: {datetime.now().strftime('%d-%m-%Y')}\n"
                    f"📘 Course: {course_info['name']}\n"
                    f"🎥 Lesson: {name}\n"
                )

                if video_url:
                    message += f"🔗 <a href=\"{video_url}\">Server Link</a>\n"
                if hd_url:
                    message += f"🔗 <a href=\"{hd_url}\">YouTube Link</a>\n"

                message += notes_links + ppt_links

                telegram_send_message(course_info["chat_id"], message)

        except Exception as e:
            print(f"[!] Error for {course_info['name']}: {e}")

def job():
    if login():
        fetch_all_courses()
        print("\n✅ Done: Messages sent to all groups.\n")

# Schedule it at 9:30 PM daily
schedule.every().day.at("21:30").do(job)

while True:
    schedule.run_pending()
    time.sleep(30)
                                               
