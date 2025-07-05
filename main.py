import requests
import schedule
import threading
import time
from datetime import datetime
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import CommandHandler, CallbackContext, Dispatcher

# Environment variables
import os
BOT_TOKEN = os.getenv("BOT_TOKEN", "7541259425:AAFcgg2q7xQ2_xoGP-eRY3G8lcfQbTOoAzM")
CHAT_ID = int(os.getenv("CHAT_ID", "6268938019"))

bot = Bot(token=BOT_TOKEN)

# User login credentials
username = "7903443604"
password = "Gautam@123"

# API URLs
LOGIN_URL = "https://admin2.khanglobalstudies.com/api/login-with-password"
LESSONS_URL = "https://admin2.khanglobalstudies.com/api/user/courses/{course_id}/v2-lessons?new=1&medium=1"

# Course list
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

# Shared headers
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Authorization": "Bearer undefined"
}

# Credit message
CREDIT_MESSAGE = "𝗧𝗛𝗜𝗦 𝗠𝗘𝗦𝗦𝗔𝗚𝗘 𝗦𝗘𝗡𝗧 𝗕𝗬 💞𝙼𝚁 𝚁𝙰𝙹𝙿𝚄𝚃💞"

# Telegram send function
def telegram_send(chat_id, text):
    try:
        bot.send_message(chat_id=chat_id, text=text[:4096], parse_mode="HTML")
        print(f"[+] Message sent to chat {chat_id}")
    except Exception as e:
        print(f"[!] Failed to send message to {chat_id}: {e}")

# Login and update token
def login():
    payload = {"phone": username, "password": password}
    try:
        r = requests.post(LOGIN_URL, headers=headers, json=payload)
        print(f"Login Response (Status {r.status_code}): {r.text}")
        if r.status_code == 200 and r.json().get("token"):
            headers["Authorization"] = f"Bearer {r.json()['token']}"
            print("[+] Login successful")
            return True
        else:
            print(f"[!] Login failed: Status {r.status_code}, Response: {r.text}")
    except Exception as e:
        print(f"[!] Login failed: {e}")
    return False

# Main fetcher function
def fetch_and_send():
    if not login():
        telegram_send(CHAT_ID, f"❌ Login failed! Check credentials.\n{CREDIT_MESSAGE}")
        return
    updates_sent = False
    for course_id, course_info in COURSES.items():
        try:
            url = LESSONS_URL.format(course_id=course_id)
            r = requests.get(url, headers=headers)
            print(f"API Response for {course_info['name']} (Status {r.status_code}): {r.text}")
            if r.status_code != 200:
                print(f"[!] HTTP Error for {course_info['name']}: Status {r.status_code}")
                continue
            try:
                data = r.json()
            except ValueError:
                print(f"[!] JSON Error for {course_info['name']}: Response is not JSON - {r.text}")
                continue
            
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
                    f"📅 Date: {datetime.now().strftime('%d-%m-%Y')}\n"
                    f"📘 Course: {course_info['name']}\n"
                    f"🎥 Lesson: {name}\n"
                )
                if video_url:
                    message += f"🔗 <a href=\"{video_url}\">Server Link</a>\n"
                if hd_url:
                    message += f"🔗 <a href=\"{hd_url}\">YouTube Link</a>\n"

                message += notes_links + ppt_links + f"\n{CREDIT_MESSAGE}"
                telegram_send(course_info["chat_id"], message)
                updates_sent = True
        except Exception as e:
            print(f"[!] Error for {course_info['name']}: {e}")
    
    if updates_sent:
        print("\n✅ Done: Messages sent to all groups.\n")
    else:
        print("\n[!] No updates to send for any course.\n")

# Flask app
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Active!"

# Webhook route
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    dispatcher = Dispatcher(bot, None, workers=0)
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("ping", ping))
    dispatcher.add_handler(CommandHandler("send", send))
    dispatcher.add_handler(CommandHandler("grpsend", grpsend))
    dispatcher.process_update(update)
    return '', 200

# Telegram bot commands
def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "/send - Send today's lessons\n/ping - Bot is alive\n/help - List commands\n/grpsend - Send updates to all groups" + f"\n{CREDIT_MESSAGE}",
        parse_mode="HTML"
    )

def ping(update: Update, context: CallbackContext):
    update.message.reply_text(f"✅ Bot is Alive!\n{CREDIT_MESSAGE}", parse_mode="HTML")

def send(update: Update, context: CallbackContext):
    if update.effective_chat.id == CHAT_ID:
        update.message.reply_text(f"📤 Sending lessons...\n{CREDIT_MESSAGE}", parse_mode="HTML")
        fetch_and_send()
    else:
        update.message.reply_text("❌ Unauthorized")

def grpsend(update: Update, context: CallbackContext):
    if update.effective_chat.id == CHAT_ID:
        update.message.reply_text(f"📤 Sending updates to all groups...\n{CREDIT_MESSAGE}", parse_mode="HTML")
        fetch_and_send()
    else:
        update.message.reply_text("❌ Unauthorized")

# Schedule 9:30 PM job
schedule.every().day.at("21:30").do(fetch_and_send)

# Send deployment notification
def send_deployment_notification():
    try:
        telegram_send(CHAT_ID, f"🚀 Bot successfully deployed on Koyeb!\n{CREDIT_MESSAGE}")
        print("[+] Deployment notification sent to CHAT_ID")
    except Exception as e:
        print(f"[!] Failed to send deployment notification: {e}")

# Start scheduler
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(10)

if __name__ == "__main__":
    send_deployment_notification()
    threading.Thread(target=run_scheduler, daemon=True).start()
    app.run()  # Koyeb डिफॉल्ट सेटिंग्स यूज करेगा
