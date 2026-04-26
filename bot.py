
import os
import logging
import telebot
from google import genai

# Loglarni sozlash
logging.basicConfig(level=logging.INFO)

# Railway Variables'dan ma'lumotlarni olish va ehtimoliy "=" belgilaridan tozalash
BOT_TOKEN = os.environ.get('BOT_TOKEN', '').replace('=', '').strip()
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '').replace('=', '').strip()

# Gemini Client yaratish
client = genai.Client(api_key=GEMINI_API_KEY)

# Telegram Botni ishga tushirish
bot = telebot.TeleBot(BOT_TOKEN)
chat_sessions = {}

SYSTEM_PROMPT = """Siz shaxsiy assistantsiz. 
Foydalanuvchi SMS yoki qo'ng'iroq buyrug'i berganda:
- SMS uchun: SMS:+998XXXXXXXXX:matn formatida javob bering
- Qo'ng'iroq uchun: CALL:+998XXXXXXXXX formatida javob bering
- Oddiy savollarga odatdagidek javob bering."""

@bot.message_handler(commands=['start'])
def start(message):
    chat_sessions[message.chat.id] = []
    bot.reply_to(message, "Salom! Men sizning shaxsiy assistantingizman!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    user_text = message.text

    if user_id not in chat_sessions:
        chat_sessions[user_id] = []

    chat_sessions[user_id].append(f"Foydalanuvchi: {user_text}")
    
    # Tarixni yig'ish
    history_text = "\n".join(chat_sessions[user_id][-10:])
    full_prompt = f"{SYSTEM_PROMPT}\n\nSuhbat tarixi:\n{history_text}"

    try:
        # Gemini 2.0 Flash modelini chaqirish
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=full_prompt
        )
        reply = response.text
    except Exception as e:
        reply = f"Gemini API xatosi: {str(e)}"
        logging.error(f"Xato yuz berdi: {e}")

    chat_sessions[user_id].append(f"Bot: {reply}")
    bot.reply_to(message, reply)

# Botni uzluksiz ishlashini ta'minlash
if __name__ == "__main__":
    logging.info("Bot ishga tushdi...")
    bot.infinity_polling()
