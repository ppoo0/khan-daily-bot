import requests
import time
from datetime import datetime
import schedule
from flask import Flask
from threading import Thread
from telegram import Update, Bot
from telegram.ext import CommandHandler, Updater, CallbackContext

# Telegram Config
BOT_TOKEN = "7541259425:AAFcgg2q7xQ2_xoGP-eRY3G8lcfQbTOoAzM"
OWNER_ID = 6268938019  # Only this user can use /send command
bot = Bot(BOT_TOKEN)

# Course Details
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

# KGS API URLs
LOGIN_URL = "https://admin2.khanglobalstudies.com/api/login-with-password"
LESSONS_URL = "https://admin2.khanglobalstudies.com/api/user/courses/{course_id}/v2-lessons?new=1&medium=1"

# Login Credentials
username = "7903443604"
password = "Gautam@123"

# Flask App to keep Koyeb instance alive
app = Flask(__name__)

@app.route('/')
def home():
    return "💞MR RAJPUT💞 Bot is running!"

def telegram_send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text[:4096],
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"[!] Telegram Error: {e}")

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Authorization": "Bearer undefined"
}

def login():
    payload = {"phone": username, "password": password}
    try:
        print("[*] Logging in...")
        r = requests.post(LOGIN_URL, headers=headers, json=payload)
        if r.status_code == 200 and r.json().get("token"):
            token = r.json()["token"]
            headers["Authorization"] = f"Bearer {token}"
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
        print("✅ Done: Messages sent to all groups.")

# Auto run job at 9:30 PM daily
schedule.every().day.at("21:30").do(job)

def schedule_loop():
    while True:
        schedule.run_pending()
        time.sleep(30)

# Telegram Command: /send (only by OWNER)
def command_listener():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher

    def send_handler(update: Update, context: CallbackContext):
        if update.effective_user.id == OWNER_ID:
            text = " ".join(context.args)
            if text:
                bot.send_message(chat_id=OWNER_ID, text=f"📤 You said:\n{text}")
            else:
                update.message.reply_text("❌ Please provide message after /send")
        else:
            update.message.reply_text("❌ Unauthorized")

    dp.add_handler(CommandHandler("send", send_handler))
    updater.start_polling()

if __name__ == '__main__':
    # 1. Notify after deployment
    telegram_send_message(OWNER_ID, "✅ Bot deployed successfully on Koyeb!\n🚀 Running now.")
    
    # 2. Start Flask server in background
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
    
    # 3. Start Telegram bot command listener
    Thread(target=command_listener).start()

    # 4. Start Scheduler loop
    schedule_loop()
