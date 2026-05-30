import os
import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='public', static_url_path='')

# 🔑 Читаем переменные окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# 🚨 Проверка переменных при старте
if not BOT_TOKEN:
    print("❌ КРИТИЧЕСКАЯ ОШИБКА: Переменная BOT_TOKEN не задана!")
if not CHAT_ID:
    print("❌ КРИТИЧЕСКАЯ ОШИБКА: Переменная CHAT_ID не задана!")

print(f"🚀 Сервер запускается...")
print(f"   BOT_TOKEN: {'✓ задан' if BOT_TOKEN else '✗ НЕ ЗАДАН'}")
print(f"   CHAT_ID: {CHAT_ID if CHAT_ID else '✗ НЕ ЗАДАН'}")
print(f"   PORT: {os.getenv('PORT', '5000 (default)')}")


# 🏠 Главная страница — раздаём index.html
@app.route('/')
def index():
    return send_from_directory('public', 'index.html')


# 📬 Эндпоинт для приёма заявок с формы
@app.route('/api/send', methods=['POST'])
def send_to_telegram():
    print("\n" + "="*60)
    print("📩 Поступил запрос POST /api/send")
    
    try:
        # Проверяем переменные
        if not BOT_TOKEN or not CHAT_ID:
            print("❌ Ошибка: Не заданы BOT_TOKEN или CHAT_ID")
            return jsonify({
                "success": False, 
                "error": "Сервер не настроен. Проверьте переменные окружения."
            }), 500

        # Получаем данные из запроса
        data = request.get_json()
        if not data:
            print("❌ Ошибка: Пустой JSON в запросе")
            return jsonify({"success": False, "error": "Нет данных в запросе"}), 400

        # Извлекаем поля
        name = data.get('name', '—')
        phone = data.get('phone', '—')
        tg = data.get('tg', '—') or 'не указан'
        biz = data.get('biz', '—') or 'не указан'
        comment = data.get('comment', '—') or 'нет'
        time = data.get('time', '—')

        print(f"👤 Данные заявки: {name} | {phone} | {biz}")

        # Формируем сообщение для Telegram
        message = (
            f"🔔 <b>Новая заявка с сайта Mbot!</b>\n\n"
            f"👤 <b>Имя:</b> {name}\n"
            f"📞 <b>Телефон:</b> {phone}\n"
            f"💬 <b>Telegram/WhatsApp:</b> {tg}\n"
            f"🏢 <b>Бизнес:</b> {biz}\n"
            f"📝 <b>Комментарий:</b> {comment}\n"
            f"🕐 <b>Время:</b> {time}"
        )

        # Отправляем в Telegram
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }

        print(f"📡 Отправляем в Telegram: chat_id={CHAT_ID}")
        
        resp = requests.post(url, json=payload, timeout=10)
        resp_data = resp.json()
        
        print(f"📡 Ответ Telegram API: {resp_data}")

        if resp.status_code == 200 and resp_data.get('ok'):
            print("✅ Заявка УСПЕШНО отправлена в Telegram!")
            print("="*60 + "\n")
            return jsonify({"success": True, "message": "Заявка отправлена"}), 200
        else:
            error_desc = resp_data.get('description', 'Неизвестная ошибка')
            print(f"❌ Ошибка Telegram: {resp.status_code} — {error_desc}")
            print("="*60 + "\n")
            return jsonify({
                "success": False, 
                "error": f"Telegram API: {error_desc}"
            }), 502

    except requests.exceptions.Timeout:
        print("❌ Таймаут при запросе к Telegram API")
        return jsonify({"success": False, "error": "Таймаут соединения"}), 504
        
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка соединения с Telegram API")
        return jsonify({"success": False, "error": "Нет соединения с Telegram"}), 503
        
    except Exception as e:
        print(f"❌ Критическая ошибка сервера: {type(e).__name__}: {e}")
        print("="*60 + "\n")
        return jsonify({"success": False, "error": f"Внутренняя ошибка: {str(e)}"}), 500


# 🧪 Тестовый эндпоинт — проверка связи с Telegram
@app.route('/test')
def test_telegram():
    print("\n" + "="*60)
    print("🧪 Запрошен тестовый эндпоинт /test")
    
    token = os.getenv('BOT_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    
    result = {
        "BOT_TOKEN": "задан" if token else "НЕ ЗАДАН",
        "CHAT_ID": chat_id if chat_id else "НЕ ЗАДАН",
        "telegram_response": None,
        "error": None
    }
    
    print(f"🔑 Token: {token[:20] + '...' if token else 'None'}")
    print(f"👤 Chat ID: {chat_id}")
    
    if not token or not chat_id:
        result["error"] = "Переменные окружения не заданы"
        print("❌ Тест прерван: нет переменных")
        print("="*60 + "\n")
        return jsonify(result), 500
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    try:
        print("📡 Отправляем тестовое сообщение...")
        resp = requests.post(url, json={
            "chat_id": chat_id,
            "text": "🟢 ТЕСТ РАБОТАЕТ! Если видите это — бот функционирует."
        }, timeout=10)
        
        resp_data = resp.json()
        result["telegram_response"] = resp_data
        result["status_code"] = resp.status_code
        
        print(f"📡 Ответ: {resp.status_code} — {resp_data}")
        
        if resp_data.get('ok'):
            print("✅ Тест УСПЕШЕН! Сообщение отправлено.")
        else:
            print(f"❌ Тест НЕ УДАЛСЯ: {resp_data.get('description')}")
            
        print("="*60 + "\n")
        return jsonify(result)
        
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        result["error"] = error_msg
        print(f"❌ Исключение: {error_msg}")
        print("="*60 + "\n")
        return jsonify(result), 500


# ℹ️ Эндпоинт для проверки статуса сервера
@app.route('/health')
def health():
    return jsonify({
        "status": "ok",
        "BOT_TOKEN": "ok" if BOT_TOKEN else "missing",
        "CHAT_ID": "ok" if CHAT_ID else "missing"
    })


# Запуск приложения
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n🎧 Слушаю порт {port} на 0.0.0.0")
    app.run(host='0.0.0.0', port=port, debug=False)
