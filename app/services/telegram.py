import requests
import os   
BOT_TOKEN =  os.getenv("TELEGRAM_KEY")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_telegram_message(chat_id: int, text: str):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }

   # print(f"[DEBUG] Enviando a chat_id={chat_id} el texto: {texto}")
  #  print(f"[DEBUG] URL: {url}")
   # print(f"[DEBUG] Payload: {payload}")

    response = requests.post(url, json=payload)

    if not response.ok:
        print(f"[ERROR] No se pudo enviar el mensaje a Telegram: {response.text}")
    
    return response.json()
