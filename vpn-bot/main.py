from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import threading
import json

load_dotenv()

app = Flask(__name__)

LARK_VERIFY_TOKEN = os.getenv("LARK_VERIFY_TOKEN")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print(f"Received: {data}")

    # Verify Lark token
    token = data.get('header', {}).get('token', '')
    if LARK_VERIFY_TOKEN and token != LARK_VERIFY_TOKEN:
        print(f"Unauthorized request — invalid token: {token}")
        return jsonify({'code': 403}), 403

    if data.get('type') == 'url_verification':
        return jsonify({'challenge': data.get('challenge')})

    threading.Thread(target=handle_event, args=(data,)).start()
    return jsonify({'code': 0})

def handle_event(data):
    try:
        event = data.get('event', {})
        message = event.get('message', {})
        msg_type = message.get('message_type', '')

        if msg_type != 'text':
            return

        content = json.loads(message.get('content', '{}'))
        text = content.get('text', '').strip()
        chat_id = message.get('chat_id', '')

        print(f"Message: {text}")
        print(f"Chat ID: {chat_id}")

        from claude_agent import run_agent
        from lark_client import send_message, send_card

        send_card(chat_id, "⏳ Processing", "Working on your request...", "grey")
        reply = run_agent(text)
        send_card(chat_id, "✅ Done", reply, "green")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        from lark_client import send_card
        send_card(chat_id, "❌ Error", str(e), "red")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
