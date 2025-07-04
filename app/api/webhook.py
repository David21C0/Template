from fastapi import APIRouter, Request
from app.core.agent import get_agent
from app.services.sender import send_whatsapp_message
from app.core.format_message import TextNormalizer
import os
from app.services.sender import send_image_message

from pydantic import BaseModel, Field
from app.services.telegram import send_telegram_message

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "ok", "message": "API is running"}

# Modelo que representa al usuario que envía el mensaje
class From(BaseModel):
    id: int

# Modelo que representa el mensaje que llega desde Telegram
class Message(BaseModel):
    from_: From = Field(..., alias="from", repr=False)
    text: str

    class Config:
        extra = "ignore"  # Ignora otros campos como chat, date, etc.
        allow_population_by_field_name = True  # Por si necesitas usar from_ en lugar de "from"

# Modelo principal que encapsula el update completo
class TelegramUpdate(BaseModel):
    message: Message

    class Config:
        extra = "ignore"

# Endpoint que recibe el webhook de Telegram
@router.post("/webhook")
async def recibir_mensaje(update: TelegramUpdate):
    user_id = update.message.from_.id
    user_text = update.message.text

    agent = get_agent(user_id)
    response = agent.run(user_text)

    if not response:
        response = "No pude procesar tu mensaje. Por favor, intenta de nuevo más tarde."
        
    send_telegram_message(chat_id=user_id, text=response)

    return {"status": "ok", "resultado": response}

"""
@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    body = await request.json()
    print("Webhook received:", body)

    try:
        message_data = body.get("messages", [])[0]
        message = message_data.get("text", {}).get("body", "")
        phone = message_data.get("from", "")
        channel_id = body.get("channel_id", "")
    except (IndexError, AttributeError, TypeError):
        return {"reply": "Formato de mensaje inválido"}

    if not message or not phone or not channel_id:
        return {"reply": "Faltan datos en el mensaje"}

    agent = get_agent(phone)
    response = agent.run(message)
    if not response:
        response = "No pude procesar tu mensaje. Por favor, intenta de nuevo más tarde."
        
    response_dict = TextNormalizer().formatear_json(response)
    respuestas = response_dict.get("json", [])
    print("Respuestas formateadas:", respuestas)
    for item in respuestas:
        message = item["message"]
        image_url = item["image"]
        if message and  image_url:
            send_image_message(phone=phone, image_url=image_url, caption=message, channel_id=channel_id)
        else:
            if message:
                send_whatsapp_message(phone=phone, message=message, channel_id=channel_id)
            if image_url:
                send_image_message(phone=phone, image_url=image_url, caption="", channel_id=channel_id)
    return {"reply": response}
"""