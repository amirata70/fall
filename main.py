import os
import telebot
from flask import Flask, request
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "123456789:ABCdefGHIjklMNOpqrsTUVwxyz_12345678")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-proj-placeholder")
WEBHOOK_BASE_URL = os.getenv("WEBHOOK_BASE_URL", "https://yourrenderapp.onrender.com")
PAYMENT_BASE_URL = os.getenv("PAYMENT_BASE_URL", "https://yourwordpress.com/payment")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Forbidden', 403


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "سلام! به ربات فال قهوه خوش آمدید ☕\n\n"
        "برای دریافت فال، لطفاً تصویر فنجان قهوه خود را ارسال کنید."
    )
    bot.reply_to(message, welcome_text)


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"

        payment_link = f"{PAYMENT_BASE_URL}?user={message.chat.id}&file_id={file_id}"

        bot.send_message(message.chat.id, "🔒 تصویر شما دریافت شد! برای دیدن فال باید پرداخت انجام بدی.")
        bot.send_message(message.chat.id, f"پرداخت از طریق لینک زیر:\n{payment_link}")
    except Exception as e:
        bot.send_message(message.chat.id, f"خطایی رخ داد: {str(e)}")


def analyze_coffee(image_url):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "یک متخصص فال قهوه هستی و بر اساس شکل‌های داخل فنجان، پیش‌بینی انجام می‌دهی."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "لطفاً فال قهوه این تصویر را تحلیل کن."},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ],
        "max_tokens": 500
    }
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=30)
        response.raise_for_status()
        res_json = response.json()
        return res_json["choices"][0]["message"]["content"]
    except Exception as e:
        return f"خطا در تحلیل تصویر: {str(e)}"


if __name__ == '__main__':
    if TOKEN and not TOKEN.startswith("123456789:ABCdef"):
        bot.remove_webhook()
        bot.set_webhook(url=f'{WEBHOOK_BASE_URL}/{TOKEN}')
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
