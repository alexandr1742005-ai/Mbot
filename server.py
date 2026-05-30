import os
import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='public', static_url_path='')

# Читаем переменные из окружения Render
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

if not BOT_TOKEN or not CHAT_ID:
    print("⚠️ ВНИМАНИЕ: BOT_TOKEN или CHAT_ID не заданы в переменных окружения!")

@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

@app.route('/api/send', methods=['POST'])
def send_to_telegram():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Нет данных'}), 400

        name = data.get('name', '—')
        phone = data.get('phone', '—')
        tg = data.get('tg', '—')
        biz = data.get('biz', '—')
        comment = data.get('comment', '—')
        time = data.get('time', '—')

        message = (
            f"🔔 <b>Новая заявка с сайта Mbot!</b>\n\n"
            f"👤 <b>Имя:</b> {name}\n"
            f"📞 <b>Телефон:</b> {phone}\n"
            f"💬 <b>Telegram/WhatsApp:</b> {tg}\n"
            f"🏢 <b>Бизнес:</b> {biz}\n"
            f"📝 <b>Комментарий:</b> {comment}\n"
            f"🕐 <b>Время:</b> {time}"
        )

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }

        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()

        print(f"✅ Заявка отправлена: {name} | {phone}")
        return jsonify({"success": True}), 200

    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Render требует привязку к 0.0.0.0
    app.run(host='0.0.0.0', port=port, debug=False)
