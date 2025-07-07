import os
import whisper
import logging
from typing import Optional, Tuple
from pydub import AudioSegment
import tempfile

logger = logging.getLogger(__name__)

class AudioProcessor:
    """
    Servicio para procesar y transcribir archivos de audio
    """
    
    def __init__(self):
        """Inicializa el procesador de audio con el modelo Whisper"""
        try:
            # Cargar el modelo Whisper (se descarga automáticamente la primera vez)
            self.model = whisper.load_model("base")
            logger.info("Modelo Whisper cargado exitosamente")
        except Exception as e:
            logger.error(f"Error al cargar el modelo Whisper: {e}")
            self.model = None
    
    def convert_audio_format(self, audio_path: str, target_format: str = "wav") -> Optional[str]:
        """
        Convierte un archivo de audio a formato WAV para mejor compatibilidad
        
        Args:
            audio_path: Ruta al archivo de audio original
            target_format: Formato de salida (por defecto WAV)
            
        Returns:
            Ruta al archivo convertido o None si hay error
        """
        try:
            # Crear archivo temporal para la conversión
            temp_dir = tempfile.gettempdir()
            filename = os.path.basename(audio_path)
            name_without_ext = os.path.splitext(filename)[0]
            converted_path = os.path.join(temp_dir, f"{name_without_ext}.{target_format}")
            
            # Cargar y convertir el audio
            audio = AudioSegment.from_file(audio_path)
            audio.export(converted_path, format=target_format)
            
            logger.info(f"Audio convertido exitosamente: {audio_path} -> {converted_path}")
            return converted_path
            
        except Exception as e:
            logger.error(f"Error al convertir audio {audio_path}: {e}")
            return None
    
    def transcribe_audio(self, audio_path: str, language: str = "es") -> Tuple[bool, str]:
        """
        Transcribe un archivo de audio a texto
        
        Args:
            audio_path: Ruta al archivo de audio
            language: Idioma del audio (por defecto español)
            
        Returns:
            Tupla (éxito, texto_transcrito_o_error)
        """
        if not self.model:
            return False, "Error: Modelo Whisper no disponible"
        
        try:
            logger.info(f"Iniciando transcripción de: {audio_path}")
            
            # Convertir a WAV si es necesario
            file_extension = os.path.splitext(audio_path)[1].lower()
            if file_extension not in ['.wav', '.wave']:
                converted_path = self.convert_audio_format(audio_path)
                if not converted_path:
                    return False, "Error al convertir el formato de audio"
                audio_path = converted_path
            
            # Transcribir con Whisper
            result = self.model.transcribe(
                audio_path,
                language=language,
                task="transcribe"
            )
            
            transcription = result["text"].strip()
            
            if transcription:
                logger.info(f"Transcripción exitosa: '{transcription[:50]}...'")
                return True, transcription
            else:
                logger.warning("Transcripción vacía - posible silencio o audio no reconocible")
                return False, "No se pudo transcribir el audio (posible silencio o audio no reconocible)"
                
        except Exception as e:
            error_msg = f"Error en transcripción: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def process_voice_message(self, audio_path: str, user_id: int) -> Tuple[bool, str]:
        """
        Procesa un mensaje de voz específicamente
        
        Args:
            audio_path: Ruta al archivo de audio del mensaje de voz
            user_id: ID del usuario para logging
            
        Returns:
            Tupla (éxito, texto_transcrito_o_error)
        """
        logger.info(f"Procesando mensaje de voz para usuario {user_id}: {audio_path}")
        
        # Los mensajes de voz de Telegram suelen ser en español
        return self.transcribe_audio(audio_path, language="es")
    
    def process_audio_file(self, audio_path: str, user_id: int) -> Tuple[bool, str]:
        """
        Procesa un archivo de audio (música, podcast, etc.)
        
        Args:
            audio_path: Ruta al archivo de audio
            user_id: ID del usuario para logging
            
        Returns:
            Tupla (éxito, texto_transcrito_o_error)
        """
        logger.info(f"Procesando archivo de audio para usuario {user_id}: {audio_path}")
        
        # Intentar detectar el idioma automáticamente
        return self.transcribe_audio(audio_path, language=None)
    
    def cleanup_temp_files(self, file_path: str):
        """
        Limpia archivos temporales creados durante el procesamiento
        
        Args:
            file_path: Ruta al archivo a eliminar
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Archivo temporal eliminado: {file_path}")
        except Exception as e:
            logger.warning(f"No se pudo eliminar archivo temporal {file_path}: {e}")

# Instancia global del procesador de audio
audio_processor = AudioProcessor() 