import requests
import schedule
import threading
import asyncio
from datetime import datetime
from flask import Flask
from telegram import Update, Bot
from telegram.ext import CommandHandler, CallbackContext, Updater

# Telegram Bot Config
BOT_TOKEN = "7541259425:AAFcgg2q7xQ2_xoGP-eRY3G8lcfQbTOoAzM"
CHAT_ID = 6268938019
bot = Bot(token=BOT_TOKEN)

# User login credentials
username = "7903443604"
password = "Gautam@123"

# API URLs
LOGIN_URL = "https://admin2.khanglobalstudies.com/api/login-with-password"
LESSONS_URL = "https://admin2.khanglobalstudies.com/api/user/courses/{course_id}/v2-lessons?new=1&medium=1"

# Course list
COURSES = {
    "696": {"name": "PSIR BY SANJAY THAKUR"},
    "686": {"name": "UPSC Mains Answer Writing Program 2025"},
    "691": {"name": "UPSC Adhyan Current Affairs (Hindi Medium) Batch 2026"},
    "704": {"name": "GEOGRAPHY OPTIONAL HINDI MEDIUM SACHIN ARORA"},
    "700": {"name": "HISTORY OPTIONAL HINDI MEDIUM"},
    "667": {"name": "UPSC (Pre + Mains) Foundation Batch 2026 Hindi Medium"},
    "670": {"name": "UPSC G.S (Prelims+Mains)फाउंडेशन प्रोग्राम 2026 हिंदी माध्यम (Offline Class) Mukherjee Nagar"},
    "617": {"name": "Pocket gk batch"},
    "372": {"name": "Geography optional english medium"}
}

# Shared headers
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Authorization": "Bearer undefined"
}

# Telegram send function
def telegram_send(text):
    bot.send_message(chat_id=CHAT_ID, text=text[:4096], parse_mode="HTML")

# Login and update token
def login():
    payload = {"phone": username, "password": password}
    try:
        r = requests.post(LOGIN_URL, headers=headers, json=payload)
        if r.status_code == 200 and r.json().get("token"):
            headers["Authorization"] = f"Bearer {r.json()['token']}"
            print("[+] Login successful")
            return True
    except Exception as e:
        print(f"[!] Login failed: {e}")
    return False

# Main fetcher function
def fetch_and_send():
    if not login():
        return
    for course_id, course_info in COURSES.items():
        try:
            url = LESSONS_URL.format(course_id=course_id)
            r = requests.get(url, headers=headers)
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

                for pdf in pdfs or []:
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
                telegram_send(message)
        except Exception as e:
            print(f"[!] Error for {course_info['name']}: {e}")

# Manual bot commands
def help_command(update: Update, context: CallbackContext):
    update.message.reply_text("/send - Send today's lessons\n/ping - Bot is alive\n/help - List commands")

def ping(update: Update, context: CallbackContext):
    update.message.reply_text("✅ Bot is Alive!")

def send(update: Update, context: CallbackContext):
    update.message.reply_text("📤 Sending lessons...")
    fetch_and_send()

def start_bot():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("ping", ping))
    dp.add_handler(CommandHandler("send", send))
    updater.start_polling()

# Schedule 9:30 PM job
schedule.every().day.at("21:30").do(fetch_and_send)

# Flask for Koyeb keepalive
app = Flask(__name__)
@app.route("/")
def home():
    return "Bot Active!"

# Threads for bot + scheduler
threading.Thread(target=start_bot).start()
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(10)
threading.Thread(target=run_scheduler).start()

# Start Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
