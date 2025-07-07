from fastapi import APIRouter, Request
from app.core.agent import get_agent
from app.services.sender import send_whatsapp_message
from app.core.format_message import TextNormalizer
import os
from app.services.sender import send_image_message

from pydantic import BaseModel, Field
from app.services.telegram import send_telegram_message, download_file
from app.services.audio_processor import audio_processor
#TODO averiguar logging typing 
from typing import List, Optional
import logging
import os
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "ok", "message": "API is running"}

# Modelo que representa al usuario que envía el mensaje
class From(BaseModel):
    id: int

# Modelo para archivos de Telegram (fotos, audios, etc.)
class TelegramFile(BaseModel):
    file_id: str
    file_unique_id: str
    file_size: Optional[int] = None
    file_path: Optional[str] = None

# Modelo para fotos
class Photo(BaseModel):
    file_id: str
    file_unique_id: str
    width: int
    height: int
    file_size: Optional[int] = None

# Modelo para archivos de audio
class Audio(BaseModel):
    file_id: str
    file_unique_id: str
    duration: int
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None

# Modelo para mensajes de voz grabados en la app de Telegram
class Voice(BaseModel):
    file_id: str
    file_unique_id: str
    duration: int
    mime_type: Optional[str] = None
    file_size: Optional[int] = None

# Modelo que representa el mensaje que llega desde Telegram
class Message(BaseModel):
    from_: From = Field(..., alias="from", repr=False)
    text: Optional[str] = None
    photo: Optional[List[Photo]] = None
    audio: Optional[Audio] = None
    voice: Optional[Voice] = None

    class Config:
        extra = "ignore"  # Ignora otros campos como chat, date, etc.
        allow_population_by_field_name = True  # Por si necesitas usar from_ en lugar de "from"

# Modelo principal que encapsula el update completo
class TelegramUpdate(BaseModel):
    message: Message

    class Config:
        extra = "ignore"

def ensure_downloads_directory():
    """Asegura que existe el directorio de descargas"""
    downloads_dir = "downloads"
    if not os.path.exists(downloads_dir):
        os.makedirs(downloads_dir)
    return downloads_dir

def process_audio_with_ai(audio_path: str, user_id: int, is_voice_message: bool = False) -> str:
    """
    Procesa un archivo de audio con IA y retorna la transcripción
    
    Args:
        audio_path: Ruta al archivo de audio
        user_id: ID del usuario
        is_voice_message: Si es un mensaje de voz (True) o archivo de audio (False)
        
    Returns:
        Texto transcrito o mensaje de error
    """
    try:
        logger.info(f"Iniciando procesamiento de audio con IA para usuario {user_id}")
        
        # Procesar el audio según el tipo
        if is_voice_message:
            success, result = audio_processor.process_voice_message(audio_path, user_id)
        else:
            success, result = audio_processor.process_audio_file(audio_path, user_id)
        
        if success:
            logger.info(f"Transcripción exitosa para usuario {user_id}: '{result[:50]}...'")
            return result
        else:
            logger.error(f"Error en transcripción para usuario {user_id}: {result}")
            return f"Error al procesar el audio: {result}"
            
    except Exception as e:
        error_msg = f"Error inesperado en procesamiento de audio: {str(e)}"
        logger.error(error_msg)
        return error_msg

# Endpoint que recibe el webhook de Telegram
@router.post("/webhook")
async def recibir_mensaje(update: TelegramUpdate):
    user_id = update.message.from_.id
    user_text = update.message.text
    photo = update.message.photo
    audio = update.message.audio
    voice = update.message.voice

    logger.info(f"Mensaje recibido de usuario {user_id}")
    logger.info(f"Tipo de contenido: texto={user_text is not None}, foto={photo is not None}, audio={audio is not None}, voice={voice is not None}")

    agent = get_agent(user_id)
    
    # Determinar el tipo de contenido recibido
    if photo:
        # Si hay foto, el agente debe responder sobre la imagen
        logger.info(f"Imagen recibida - File ID: {photo[0].file_id if photo else 'N/A'}")
        response = agent.run("imagen recibida")
        
    elif voice:
        # Si hay mensaje de voz grabado en la app, procesar con IA
        logger.info(f"Mensaje de voz recibido - File ID: {voice.file_id}, Duración: {voice.duration}s")
        
        # Descargar el archivo de voz
        downloads_dir = ensure_downloads_directory()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        voice_filename = f"voice_{user_id}_{timestamp}.ogg"
        voice_path = os.path.join(downloads_dir, voice_filename)
        
        voice_content = download_file(voice.file_id, voice_path)
        if voice_content:
            logger.info(f"Mensaje de voz descargado exitosamente: {voice_path}")
            
            # Procesar con IA para transcribir
            transcription = process_audio_with_ai(voice_path, user_id, is_voice_message=True)
            
            if transcription and not transcription.startswith("Error"):
                # Pasar la transcripción al agente y formatear la respuesta
                logger.info(f"Enviando transcripción al agente: '{transcription[:50]}...'")
                agent_response = agent.run(transcription)
                response = f'"{transcription}" : {agent_response}'
            else:
                # Si hay error en transcripción, responder apropiadamente
                response = f"No pude entender tu mensaje de voz. {transcription}"
        else:
            logger.error(f"No se pudo descargar el mensaje de voz: {voice.file_id}")
            response = "No pude procesar tu mensaje de voz. Por favor, intenta de nuevo."
        
    elif audio:
        # Si hay archivo de audio, procesar con IA
        logger.info(f"Archivo de audio recibido - File ID: {audio.file_id}, Duración: {audio.duration}s")
        
        # Descargar el archivo de audio
        downloads_dir = ensure_downloads_directory()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if audio.file_name:
            audio_filename = f"audio_{user_id}_{timestamp}_{audio.file_name}"
        else:
            audio_filename = f"audio_{user_id}_{timestamp}.mp3"
        
        audio_path = os.path.join(downloads_dir, audio_filename)
        
        audio_content = download_file(audio.file_id, audio_path)
        if audio_content:
            logger.info(f"Archivo de audio descargado exitosamente: {audio_path}")
            
            # Procesar con IA para transcribir
            transcription = process_audio_with_ai(audio_path, user_id, is_voice_message=False)
            
            if transcription and not transcription.startswith("Error"):
                # Pasar la transcripción al agente y formatear la respuesta
                logger.info(f"Enviando transcripción al agente: '{transcription[:50]}...'")
                agent_response = agent.run(transcription)
                response = f'"{transcription}" : {agent_response}'
            else:
                # Si hay error en transcripción, responder apropiadamente
                response = f"No pude procesar el contenido de audio. {transcription}"
        else:
            logger.error(f"No se pudo descargar el archivo de audio: {audio.file_id}")
            response = "No pude procesar tu archivo de audio. Por favor, intenta de nuevo."
        
    elif user_text:
        # Si hay texto, procesar normalmente
        logger.info(f"Texto recibido: {user_text}")
        response = agent.run(user_text)
    else:
        # Si no hay contenido reconocido
        logger.warning("Tipo de contenido no reconocido")
        response = "No pude identificar el tipo de contenido enviado."

    if not response:
        response = "No pude procesar tu mensaje. Por favor, intenta de nuevo más tarde."
 #TODO averiguar logger
    logger.info(f"Respuesta del agente: {response}")
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