import requests
import config
BOT_TOKEN = config.TELEGRAM_KEY
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def enviar_mensaje_telegram(chat_id: int, texto: str):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": texto
    }

   # print(f"[DEBUG] Enviando a chat_id={chat_id} el texto: {texto}")
  #  print(f"[DEBUG] URL: {url}")
   # print(f"[DEBUG] Payload: {payload}")

    response = requests.post(url, json=payload)

    if not response.ok:
        print(f"[ERROR] No se pudo enviar el mensaje a Telegram: {response.text}")
    
    return response.json()
