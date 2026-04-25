import os
import logging
import telebot
from google import genai

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

client = genai.Client(api_key=GEMINI_API_KEY)

bot = telebot.TeleBot(BOT_TOKEN)
chat_sessions = {}

SYSTEM_PROMPT = """Siz shaxsiy Jarvis assistantsiz. 
Foydalanuvchi SMS yoki qo'ng'iroq buyrug'i berganda:
- SMS uchun: [SMS:+998XXXXXXXXX:matn] formatida javob bering
- Qo'ng'iroq uchun: [CALL:+998XXXXXXXXX] formatida javob bering
- Oddiy savollarga odatdagidek javob bering."""

@bot.message_handler(commands=['start'])
def start(message):
    chat_sessions[message.chat.id] = []
    bot.reply_to(message, "Salom! Men sizning shaxsiy Jarvis assistantingizman!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    user_text = message.text

    if user_id not in chat_sessions:
        chat_sessions[user_id] = []

    # Tarixga qo'shish
    chat_sessions[user_id].append({
        "role": "user",
        "parts": [user_text]
    })

    # So'rov yuborish
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=[{"role": "user", "parts": [SYSTEM_PROMPT]}] + chat_sessions[user_id]
    )

    reply = response.text

    # Bot javobini tarixga qo'shish
    chat_sessions[user_id].append({
        "role": "model",
        "parts": [reply]
    })

    bot.reply_to(message, reply)

bot.polling()
