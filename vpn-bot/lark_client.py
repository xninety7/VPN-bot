import requests
import os
import json

def get_token():
    url = "https://open.larksuite.com/open-apis/auth/v3/tenant_access_token/internal"
    res = requests.post(url, json={
        "app_id": os.getenv("LARK_APP_ID"),
        "app_secret": os.getenv("LARK_APP_SECRET")
    })
    return res.json().get('tenant_access_token')

def send_message(chat_id, text):
    token = get_token()
    url = "https://open.larksuite.com/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "receive_id": chat_id,
        "receive_id_type": "chat_id",
        "msg_type": "text",
        "content": json.dumps({"text": text})
    }
    res = requests.post(url, headers=headers, params={"receive_id_type": "chat_id"}, json=payload)
    print(f"Lark response: {res.json()}")

def send_card(chat_id, title, content, color="blue"):
    token = get_token()
    url = "https://open.larksuite.com/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    card = {
        "config": { "wide_screen_mode": True },
        "header": {
            "title": { "tag": "plain_text", "content": title },
            "template": color
        },
        "elements": [
            {
                "tag": "div",
                "text": { "tag": "lark_md", "content": content }
            }
        ]
    }
    payload = {
        "receive_id": chat_id,
        "receive_id_type": "chat_id",
        "msg_type": "interactive",
        "content": json.dumps(card)
    }
    res = requests.post(url, headers=headers, params={"receive_id_type": "chat_id"}, json=payload)
    print(f"Lark card response: {res.json()}")
