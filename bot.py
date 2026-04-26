import os
import logging
import telebot
import requests
from groq import Groq

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
MACRODROID_CALL_WEBHOOK = "https://trigger.macrodroid.com/28493cc3-e6c4-4e3c-bdfd-6a5420bf28a0/call"

client = Groq(api_key=GROQ_API_KEY)

bot = telebot.TeleBot(BOT_TOKEN)
chat_sessions = {}

SYSTEM_PROMPT = """Siz shaxsiy Gitler assistantsiz. 
Foydalanuvchi SMS yoki qo'ng'iroq buyrug'i berganda:
- SMS uchun: SMS:+998XXXXXXXXX:matn formatida javob bering
- Qo'ng'iroq uchun: CALL:+998XXXXXXXXX formatida javob bering
- Oddiy savollarga odatdagidek javob bering."""

@bot.message_handler(commands=['start'])
def start(message):
    chat_sessions[message.chat.id] = []
    bot.reply_to(message, "Salom! Men sizning shaxsiy Gitler assistantingizman!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    user_text = message.text

    if user_id not in chat_sessions:
        chat_sessions[user_id] = []

    chat_sessions[user_id].append({
        "role": "user",
        "content": user_text
    })

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + chat_sessions[user_id][-10:]

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = f"Xato: {str(e)}"
        logging.error(e)

    chat_sessions[user_id].append({
        "role": "assistant",
        "content": reply
    })

    # CALL webhook
    if reply.startswith("CALL:"):
        number = reply.replace("CALL:", "").strip()
        try:
            requests.post(MACRODROID_CALL_WEBHOOK, data=number)
            logging.info(f"Webhook yuborildi: {number}")
        except Exception as e:
            logging.error(f"Webhook xato: {e}")

    bot.reply_to(message, reply)

if __name__ == "__main__":
    logging.info("Bot ishga tushdi...")
    import time
    time.sleep(5)
    bot.infinity_polling(skip_pending=True)
