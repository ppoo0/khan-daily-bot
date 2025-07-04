import requests
import schedule
import threading
import time
from datetime import datetime
from flask import Flask
from telegram import Bot, Update
from telegram.ext import CommandHandler, Updater

BOT_TOKEN = "7541259425:AAFcgg2q7xQ2_xoGP-eRY3G8lcfQbTOoAzM"
OWNER_CHAT_ID = 6268938019

bot = Bot(BOT_TOKEN)
updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

app = Flask(__name__)

# Sample course IDs and names (for demo)
COURSES = {
    "1283": "PSIR BY SANJAY THAKUR",
    "1284": "UPSC Mains Answer Writing Program 2025",
    "1285": "UPSC Adhyan Current Affairs (Hindi Medium) Batch 2026",
    "1286": "GEOGRAPHY OPTIONAL HINDI MEDIUM SACHIN ARORA",
    "1287": "HISTORY OPTIONAL HINDI MEDIUM",
    "1288": "UPSC (Pre + Mains) Foundation Batch 2026 Hindi Medium",
    "1289": "UPSC G.S (Prelims+Mains)फाउंडेशन प्रोग्राम 2026 हिंदी माध्यम",
    "1290": "Pocket gk batch",
    "1291": "Geography optional english medium"
}

# Function to get updates for a single course
def fetch_course_updates(course_id, course_name):
    try:
        url = f"https://app.khanglobalstudies.com/api/course-lessons?course_id={course_id}"
        res = requests.get(url)
        data = res.json()

        lessons = data.get("data", {}).get("course", {}).get("lessons", [])
        if not lessons:
            print(f"[-] No new lessons for {course_name}")
            return ""

        message = f"<b>{course_name}</b>\n"
        for lesson in lessons[-3:]:  # latest 3 lessons
            title = lesson.get("title", "No Title")
            class_link = lesson.get("video", {}).get("video_url", "")
            message += f"\n<b>{title}</b>\n"
            if class_link:
                message += f"<a href='{class_link}'>Watch Now</a>\n"
            for file in lesson.get("pdfs", []):
                fname = file.get("name", "PDF")
                furl = file.get("url", "")
                message += f"<a href='{furl}'>{fname}</a>\n"

        return message.strip() + "\n"

    except Exception as e:
        print(f"[!] Error for {course_name}: {e}")
        return ""

# Function to send updates to all courses
def send_daily_updates():
    final_msg = ""
    for cid, cname in COURSES.items():
        msg = fetch_course_updates(cid, cname)
        if msg:
            final_msg += msg + "\n"

    if final_msg:
        bot.send_message(chat_id=OWNER_CHAT_ID, text=final_msg, parse_mode='HTML', disable_web_page_preview=True)
        print("\n\u2705 Done: Messages sent to all groups.\n")
    else:
        print("\n[!] No updates to send.\n")

# Flask root ping
@app.route("/")
def home():
    return "Bot Running..."

# Scheduler job for 9:30 PM daily
def schedule_job():
    schedule.every().day.at("21:30").do(send_daily_updates)
    while True:
        schedule.run_pending()
        time.sleep(1)

# --- Telegram Command Handlers ---
def ping(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Bot is alive!")

def help_cmd(update, context):
    help_text = "/ping - Check if bot is alive\n/send - Manually send today's updates to you\n/grpsend - Send updates to all groups manually"
    context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)

def send(update, context):
    if update.effective_chat.id == OWNER_CHAT_ID:
        send_daily_updates()
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Unauthorized")

def grpsend(update, context):
    if update.effective_chat.id == OWNER_CHAT_ID:
        send_daily_updates()
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Unauthorized")

# Add handlers
dispatcher.add_handler(CommandHandler("ping", ping))
dispatcher.add_handler(CommandHandler("help", help_cmd))
dispatcher.add_handler(CommandHandler("send", send))
dispatcher.add_handler(CommandHandler("grpsend", grpsend))

# Start scheduler and bot in threads
def start_scheduler():
    threading.Thread(target=schedule_job).start()

def start_bot():
    threading.Thread(target=updater.start_polling).start()

if __name__ == "__main__":
    start_scheduler()
    start_bot()
    app.run(host='0.0.0.0', port=8080)
    
