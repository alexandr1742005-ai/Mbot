from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Токен и Chat ID берутся из переменных окружения — НЕ из кода!
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHAT_IDS = os.environ.get("CHAT_IDS", "").split(",")

@app.route("/")
def index():
    return open("index.html", "r", encoding="utf-8").read()

@app.route("/api/send", methods=["POST"])
def send():
    data = request.get_json()

    name = data.get("name", "—")
    phone = data.get("phone", "—")
    tg = data.get("tg", "—")
    biz = data.get("biz", "—")
    comment = data.get("comment", "—")

    msg = (
        f"📨 <b>Новая заявка с сайта Mbot</b>\n\n"
        f"👤 <b>Имя:</b> {name}\n"
        f"📱 <b>Телефон:</b> {phone}\n"
        f"💬 <b>Telegram:</b> {tg}\n"
        f"🏢 <b>Бизнес:</b> {biz}\n"
        f"📝 <b>Комментарий:</b> {comment}\n\n"
        f"🕐 {data.get('time', '—')}"
    )

    results = []
    for chat_id in CHAT_IDS:
        chat_id = chat_id.strip()
        if not chat_id:
            continue
        try:
            resp = requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": msg, "parse_mode": "HTML"},
                timeout=10
            )
            results.append({"chat_id": chat_id, "ok": resp.json().get("ok", False)})
        except Exception as e:
            results.append({"chat_id": chat_id, "ok": False, "error": str(e)})

    return jsonify({"results": results})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
