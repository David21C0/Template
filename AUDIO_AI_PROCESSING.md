# Procesamiento de Audio con IA - Segunda Capa de Inteligencia

## Descripción

Se ha implementado una **segunda capa de IA** que procesa automáticamente los archivos de audio y mensajes de voz recibidos desde Telegram. Esta capa utiliza **OpenAI Whisper** para transcribir el audio a texto, que luego se pasa al agente principal para generar respuestas contextuales.

## Arquitectura del Sistema

```
Usuario envía audio → Telegram → Webhook → Descarga archivo → Whisper (IA) → Transcripción → Agente Principal → Respuesta
```

### Flujo Detallado

1. **Usuario envía mensaje de voz o archivo de audio** a través de Telegram
2. **Telegram envía webhook** con metadata del archivo (file_id)
3. **Sistema descarga el archivo** usando la API de Telegram
4. **Whisper procesa el audio** y genera transcripción
5. **Texto transcrito se envía al agente** principal
6. **Agente genera respuesta** contextual
7. **Respuesta se envía de vuelta** al usuario

## Componentes Implementados

### 1. AudioProcessor (`app/services/audio_processor.py`)

Servicio principal que maneja:
- **Carga del modelo Whisper** (base, medium, large)
- **Conversión de formatos** de audio (MP3, OGG, WAV, etc.)
- **Transcripción automática** con detección de idioma
- **Manejo de errores** y logging detallado

```python
from app.services.audio_processor import audio_processor

# Procesar mensaje de voz
success, transcription = audio_processor.process_voice_message(audio_path, user_id)

# Procesar archivo de audio
success, transcription = audio_processor.process_audio_file(audio_path, user_id)
```

### 2. Integración en Webhook (`app/api/webhook.py`)

El webhook ahora:
- **Detecta automáticamente** mensajes de voz y archivos de audio
- **Descarga los archivos** de Telegram
- **Procesa con Whisper** para obtener transcripción
- **Pasa el texto al agente** para respuesta contextual
- **Maneja errores** de transcripción apropiadamente

### 3. Prompt Actualizado (`app/core/prompts.py`)

El agente ahora sabe que:
- Puede recibir **mensajes de voz transcritos**
- Debe responder **naturalmente** como si fuera texto escrito
- Los mensajes de voz se **procesan automáticamente**

## Tipos de Audio Soportados

### Mensajes de Voz (`voice`)
- **Formato**: OGG (Telegram)
- **Idioma**: Español (configurado)
- **Uso**: Conversaciones naturales
- **Ejemplo**: "Hola, quiero hacer una reserva"

### Archivos de Audio (`audio`)
- **Formatos**: MP3, WAV, FLAC, M4A, etc.
- **Idioma**: Detección automática
- **Uso**: Podcasts, música con voz, etc.
- **Ejemplo**: Archivo de podcast sobre restaurantes

## Configuración

### 1. Instalar Dependencias

```bash
pip install openai-whisper pydub ffmpeg-python
```

### 2. Instalar FFmpeg (Requerido por Whisper)

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
```bash
# Descargar desde https://ffmpeg.org/download.html
# O usar chocolatey: choco install ffmpeg
```

### 3. Modelos de Whisper

El sistema usa el modelo **"base"** por defecto:
- **Ventajas**: Rápido, ligero (74MB)
- **Desventajas**: Menos preciso que modelos más grandes

Para cambiar el modelo, edita `app/services/audio_processor.py`:

```python
# Cambiar de "base" a "medium" o "large"
self.model = whisper.load_model("medium")  # 769MB, más preciso
```

## Ejemplos de Uso

### Ejemplo 1: Mensaje de Voz
```
Usuario: [Graba mensaje de voz] "Hola, quiero reservar una mesa para 4 personas mañana a las 8pm"

Sistema:
1. Descarga archivo OGG
2. Whisper transcribe: "Hola, quiero reservar una mesa para 4 personas mañana a las 8pm"
3. Agente responde: "¡Perfecto! Te ayudo con tu reserva. ¿Podrías darme tu nombre y dirección?"
```

### Ejemplo 2: Archivo de Audio
```
Usuario: [Envía archivo MP3 con podcast sobre restaurantes]

Sistema:
1. Descarga archivo MP3
2. Whisper transcribe contenido del podcast
3. Agente responde contextualmente sobre el contenido
```

## Logging y Debugging

El sistema incluye logging detallado:

```
INFO: Mensaje de voz recibido - File ID: voice_123, Duración: 15s
INFO: Mensaje de voz descargado exitosamente: downloads/voice_456_20241201_143022.ogg
INFO: Iniciando procesamiento de audio con IA para usuario 123456789
INFO: Iniciando transcripción de: downloads/voice_456_20241201_143022.ogg
INFO: Transcripción exitosa para usuario 123456789: 'Hola, quiero hacer una reserva...'
INFO: Enviando transcripción al agente: 'Hola, quiero hacer una reserva...'
INFO: Respuesta del agente: ¡Perfecto! Te ayudo con tu reserva...
```

## Pruebas

### Script de Prueba Automatizado

```bash
python test_audio_transcription.py
```

Este script:
- Verifica instalación de Whisper
- Prueba el procesador de audio
- Crea archivos de prueba
- Prueba transcripción con archivos existentes

### Pruebas Manuales

1. **Enviar mensaje de voz** al bot de Telegram
2. **Enviar archivo de audio** al bot
3. **Verificar transcripción** en los logs
4. **Confirmar respuesta** contextual del agente

## Consideraciones de Rendimiento

### Tiempo de Procesamiento
- **Modelo base**: ~2-5 segundos por minuto de audio
- **Modelo medium**: ~5-10 segundos por minuto de audio
- **Modelo large**: ~10-20 segundos por minuto de audio

### Uso de Memoria
- **Modelo base**: ~1GB RAM
- **Modelo medium**: ~2GB RAM
- **Modelo large**: ~4GB RAM

### Límites de Archivo
- **Mensajes de voz**: Hasta 20MB
- **Archivos de audio**: Hasta 50MB
- **Duración recomendada**: Hasta 10 minutos

## Solución de Problemas

### Error: "No se pudo transcribir el audio"
- Verificar que FFmpeg esté instalado
- Comprobar formato del archivo
- Revisar logs para errores específicos

### Error: "Modelo Whisper no disponible"
- Verificar instalación: `pip install openai-whisper`
- Comprobar conexión a internet (para descargar modelo)
- Revisar permisos de escritura

### Transcripción vacía
- Audio puede ser silencio
- Calidad de audio muy baja
- Idioma no reconocido

## Próximas Mejoras

- [ ] **Transcripción en tiempo real** (streaming)
- [ ] **Detección de emociones** en la voz
- [ ] **Soporte para múltiples idiomas** automático
- [ ] **Compresión de audio** para archivos grandes
- [ ] **Cache de transcripciones** para archivos repetidos
- [ ] **Análisis de sentimiento** del audio 