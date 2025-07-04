import requests
import schedule
import threading
import time
from datetime import datetime
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import CommandHandler, Updater, Dispatcher

BOT_TOKEN = "7541259425:AAFcgg2q7xQ2_xoGP-eRY3G8lcfQbTOoAzM"
OWNER_CHAT_ID = 6268938019

bot = Bot(BOT_TOKEN)
updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

app = Flask(__name__)

# Updated COURSES dictionary with course names and chat IDs
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

# Function to get updates for a single course
def fetch_course_updates(course_id, course_name):
    try:
        url = f"https://app.khanglobalstudies.com/api/course-lessons?course_id={course_id}"
        res = requests.get(url)
        print(f"API Response for {course_name} (Status {res.status_code}): {res.text}")
        if res.status_code != 200:
            print(f"[!] HTTP Error for {course_name}: Status {res.status_code}")
            return ""
        try:
            data = res.json()
        except ValueError:
            print(f"[!] JSON Error for {course_name}: Response is not JSON - {res.text}")
            return ""
        
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

# Function to send updates to respective course chat IDs
def send_daily_updates():
    for cid, course_info in COURSES.items():
        course_name = course_info["name"]
        chat_id = course_info["chat_id"]
        msg = fetch_course_updates(cid, course_name)
        if msg:
            try:
                bot.send_message(chat_id=chat_id, text=msg, parse_mode='HTML', disable_web_page_preview=True)
                print(f"[+] Sent updates for {course_name} to chat {chat_id}")
            except Exception as e:
                print(f"[!] Failed to send message to {chat_id} for {course_name}: {e}")
        else:
            print(f"[!] No updates to send for {course_name}")

    print("\n✅ Done: Messages sent to all groups.\n")

# Flask root ping
@app.route("/")
def home():
    return "Bot Running..."

# Webhook route for Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    dispatcher.process_update(update)
    return '', 200

# Scheduler job for 9:30 PM daily
def schedule_job():
    schedule.every().day.at("21:30").do(send_daily_updates)
    while True:
        schedule.run_pending()
        time.sleep(1)

# Telegram Command Handlers
def ping(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Bot is alive!")

def help_cmd(update, context):
    help_text = "/ping - Check if bot is alive\n/send - Manually send today's updates to you\n/grpsend - Send updates to all groups manually"
    context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)

def send(update, context):
    if update.effective_chat.id == OWNER_CHAT_ID:
        send_daily_updates()
        context.bot.send_message(chat_id=update.effective_chat.id, text="Updates sent to respective groups!")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Unauthorized")

def grpsend(update, context):
    if update.effective_chat.id == OWNER_CHAT_ID:
        send_daily_updates()
        context.bot.send_message(chat_id=update.effective_chat.id, text="Updates sent to all groups!")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Unauthorized")

# Error handler for Telegram
def error_handler(update, context):
    print(f"[!] Telegram Error: {context.error}")

# Add handlers
dispatcher.add_handler(CommandHandler("ping", ping))
dispatcher.add_handler(CommandHandler("help", help_cmd))
dispatcher.add_handler(CommandHandler("send", send))
dispatcher.add_handler(CommandHandler("grpsend", grpsend))
dispatcher.add_error_handler(error_handler)

# Set webhook
def set_webhook():
    webhook_url = 'https://your-app.koyeb.app/webhook'  # Replace with your Koyeb app URL
    bot.set_webhook(webhook_url)
    print(f"[+] Webhook set to {webhook_url}")

# Start scheduler and bot
def start_scheduler():
    threading.Thread(target=schedule_job, daemon=True).start()

if __name__ == "__main__":
    set_webhook()  # Set webhook instead of polling
    start_scheduler()
    app.run(host='0.0.0.0', port=8080)
