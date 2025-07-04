import requests
import schedule
import threading
import time
from datetime import datetime
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import CommandHandler, CallbackContext, Updater, Dispatcher

import os
BOT_TOKEN = os.getenv("BOT_TOKEN", "7541259425:AAFcgg2q7xQ2_xoGP-eRY3G8lcfQbTOoAzM")
CHAT_ID = int(os.getenv("CHAT_ID", "6268938019"))
bot = Bot(token=BOT_TOKEN)

username = "7903443604"
password = "Gautam@123"
LOGIN_URL = "https://admin2.khanglobalstudies.com/api/login-with-password"
LESSONS_URL = "https://admin2.khanglobalstudies.com/api/user/courses/{course_id}/v2-lessons?new=1&medium=1"
COURSES = {"696": {"name": "PSIR BY SANJAY THAKUR", "chat_id": "-1002898647258"}, ...}  # Shortened
headers = {"Accept": "application/json", "Content-Type": "application/json", "Access-Control-Allow-Origin": "*", "Authorization": "Bearer undefined"}
CREDIT_MESSAGE = "𝗧𝗛𝗜𝗦 𝗠𝗘𝗦𝗦𝗔𝗚𝗘 𝗦𝗘𝗡𝗧 𝗕𝗬 💞𝙼𝚁 𝚁𝙰𝙹𝙿𝚄𝚃💞"

def telegram_send(chat_id, text):
    try: bot.send_message(chat_id=chat_id, text=text[:4096], parse_mode="HTML"); print(f"[+] Message sent to {chat_id}")
    except Exception as e: print(f"[!] Failed: {e}")

def login():  # Same as before
    payload = {"phone": username, "password": password}
    try: r = requests.post(LOGIN_URL, headers=headers, json=payload); print(f"Login: {r.status_code} {r.text}")
        if r.status_code == 200 and r.json().get("token"): headers["Authorization"] = f"Bearer {r.json()['token']}; return True"
        else: print("[!] Login failed"); return False
    except: print("[!] Login error"); return False

def fetch_and_send():  # Same as before
    if not login(): telegram_send(CHAT_ID, f"❌ Login failed!\n{CREDIT_MESSAGE}"); return
    for course_id, course_info in COURSES.items():
        try: r = requests.get(LESSONS_URL.format(course_id=course_id), headers=headers); print(f"API: {course_info['name']} {r.status_code} {r.text}")
            if r.status_code != 200: continue
            data = r.json(); today_classes = data.get("todayclasses", [])
            if not today_classes: continue
            for cls in today_classes:
                message = f"📅 {datetime.now().strftime('%d-%m-%Y')}\n📘 {course_info['name']}\n🎥 {cls.get('name', 'No Name')}\n"
                if cls.get("video_url"): message += f"🔗 <a href='{cls['video_url']}'>Server</a>\n"
                if cls.get("hd_video_url"): message += f"🔗 <a href='{cls['hd_video_url']}'>YouTube</a>\n"
                for pdf in cls.get("pdfs", []): message += f"{'📝' if 'ppt' not in pdf.get('title', '').lower() else '📄'} <a href='{pdf['url']}'>{pdf.get('title', 'File')}</a>\n"
                telegram_send(course_info["chat_id"], message + f"\n{CREDIT_MESSAGE}")
        except Exception as e: print(f"[!] Error: {course_info['name']} {e}")

app = Flask(__name__)
@app.route("/") def home(): return "Bot Active!"
@app.route('/webhook', methods=['POST']) def webhook(): update = Update.de_json(request.get_json(), bot); updater.dispatcher.process_update(update); return '', 200

def help_command(update, context): update.message.reply_text(f"/send /ping /help /grpsend\n{CREDIT_MESSAGE}", parse_mode="HTML")
def ping(update, context): update.message.reply_text(f"✅ Bot Alive!\n{CREDIT_MESSAGE}", parse_mode="HTML")
def send(update, context): if update.effective_chat.id == CHAT_ID: update.message.reply_text(f"📤 Sending...\n{CREDIT_MESSAGE}", parse_mode="HTML"); fetch_and_send()
def grpsend(update, context): if update.effective_chat.id == CHAT_ID: update.message.reply_text(f"📤 Sending all...\n{CREDIT_MESSAGE}", parse_mode="HTML"); fetch_and_send()

schedule.every().day.at("21:30").do(fetch_and_send)
def send_deployment_notification(): telegram_send(CHAT_ID, f"🚀 Deployed!\n{CREDIT_MESSAGE}"); print("[+] Notif sent")
def set_webhook(): bot.set_webhook('https://relaxed-vannie-asew-a4c78a9c.koyeb.app/webhook'); print("[+] Webhook set")
def run_scheduler(): while True: schedule.run_pending(); time.sleep(10)
def start_bot():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("ping", ping))
    dp.add_handler(CommandHandler("send", send))
    dp.add_handler(CommandHandler("grpsend", grpsend))
    dp.add_error_handler(lambda u, c: print(f"[!] Error: {c.error}"))
    updater.start_webhook(listen="0.0.0.0", port=443, url_path="webhook")  # Changed to 443
    updater.bot.set_webhook('https://relaxed-vannie-asew-a4c78a9c.koyeb.app/webhook')
    print("[+] Webhook started")
    return updater

if __name__ == "__main__":
    set_webhook()
    send_deployment_notification()
    updater = start_bot()
    threading.Thread(target=run_scheduler, daemon=True).start()
    app.run(host="0.0.0.0", port=443)  # Changed to 443
