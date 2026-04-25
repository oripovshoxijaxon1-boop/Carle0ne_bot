import os
import logging
import telebot
import google.generativeai as genai
import re

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = telebot.TeleBot(BOT_TOKEN)
chat_sessions = {}

SYSTEM_PROMPT = """Siz shaxsiy Jarvis assistantsiz. 
Foydalanuvchi SMS yoki qo'ng'iroq buyrug'i berganda:
- SMS uchun: [SMS:+998XXXXXXXXX:matn] formatida javob bering
- Qo'ng'iroq uchun: [CALL:+998XXXXXXXXX] formatida javob bering
- Oddiy savollarga odatdagidek javob bering."""

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom! Men sizning shaxsiy Jarvis assistantingizman! Nima qila olishimni so'rang!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    user_text = message.text
    if user_id not in chat_sessions:
        chat_sessions[user_id] = model.start_chat(history=[])
    full_prompt = SYSTEM_PROMPT + "\n\nFoydalanuvchi: " + user_text
    response = chat_sessions[user_id].send_message(full_prompt)
    bot.reply_to(message, response.text)

bot.polling()
