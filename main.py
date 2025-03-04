import telebot
from flask import Flask, request
import openai
import requests

TOKEN = "توکن_ربات_تلگرام"
OPENAI_API_KEY = "کلید_API_OpenAI"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'OK', 200

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
    
    # ارسال عکس به OpenAI برای تحلیل
    analysis = analyze_coffee(file_url)
    
    # ارسال لینک پرداخت
    bot.send_message(message.chat.id, "🔒 برای دیدن فال باید پرداخت انجام بدی!")
    payment_link = f"https://yourwordpress.com/payment?user={message.chat.id}"
    bot.send_message(message.chat.id, f"پرداخت از طریق لینک زیر:\n{payment_link}")

def analyze_coffee(image_url):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {"role": "system", "content": "یک متخصص فال قهوه هستی و بر اساس شکل‌های داخل فنجان، پیش‌بینی انجام می‌دهی."},
            {"role": "user", "content": f"لطفاً فال قهوه این تصویر را تحلیل کن: {image_url}"}
        ],
        "max_tokens": 200
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]

bot.remove_webhook()
bot.set_webhook(url=f'https://yourrenderapp.onrender.com/{TOKEN}')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
