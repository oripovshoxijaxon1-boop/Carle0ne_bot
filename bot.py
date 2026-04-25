import os
import logging
import telebot
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = telebot.TeleBot(BOT_TOKEN)

chat_sessions = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom! Men sizning shaxsiy Jarvis assistantingizman! Nima qila olishimni so'rang!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    user_text = message.text
    
    if user_id not in chat_sessions:
        chat_sessions[user_id] = model.start_chat(history=[])
    
    response = chat_sessions[user_id].send_message(user_text)
    bot.reply_to(message, response.text)

bot.polling()
