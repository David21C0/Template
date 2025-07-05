# Cómo Llega el Audio en el Request de Telegram

## Estructura del Request

Cuando Telegram envía un mensaje con audio, **NO** llega como URL directa, sino como **metadata** que incluye un `file_id`. Aquí te explico el proceso completo:

## 1. Request Inicial (Webhook)

### Para Archivo de Audio (`audio`)
```json
{
  "message": {
    "from": {"id": 123456789},
    "audio": {
      "file_id": "CQACAgIAAxkBAAIBY2Q...", // ID único del archivo
      "file_unique_id": "AgADAgADAAEC",
      "duration": 180,
      "file_name": "mi_cancion.mp3",
      "mime_type": "audio/mpeg",
      "file_size": 2048000
    }
  }
}
```

### Para Mensaje de Voz (`voice`)
```json
{
  "message": {
    "from": {"id": 123456789},
    "voice": {
      "file_id": "AwACAgIAAxkBAAIBY2Q...", // ID único del archivo
      "file_unique_id": "AgADAwACAAEC",
      "duration": 15,
      "mime_type": "audio/ogg",
      "file_size": 256000
    }
  }
}
```

## 2. Proceso para Obtener el Archivo

### Paso 1: Obtener Información del Archivo
Usando el `file_id`, haces una petición a la API de Telegram:

```python
# GET https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}
response = {
  "ok": true,
  "result": {
    "file_id": "CQACAgIAAxkBAAIBY2Q...",
    "file_unique_id": "AgADAgADAAEC",
    "file_size": 2048000,
    "file_path": "voice/file_123.ogg" // Ruta del archivo en servidores de Telegram
  }
}
```

### Paso 2: Construir URL de Descarga
Con el `file_path` obtenido, construyes la URL de descarga:

```
https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}
```

**Ejemplo:**
```
https://api.telegram.org/file/bot123456789:ABCdefGHIjklMNOpqrsTUVwxyz/file_123.ogg
```

## 3. Implementación en el Código

### Función para Obtener Información del Archivo
```python
def get_file_info(file_id: str):
    url = f"{BASE_URL}/getFile"
    payload = {"file_id": file_id}
    
    response = requests.post(url, json=payload)
    
    if response.ok:
        return response.json()
    else:
        print(f"[ERROR] No se pudo obtener información del archivo: {response.text}")
        return None
```

### Función para Descargar el Archivo
```python
def download_file(file_id: str, save_path: str = None):
    file_info = get_file_info(file_id)
    
    if not file_info or not file_info.get("ok"):
        return None
    
    file_path = file_info["result"]["file_path"]
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    
    response = requests.get(file_url)
    
    if response.ok:
        if save_path:
            with open(save_path, 'wb') as f:
                f.write(response.content)
        return response.content
    else:
        print(f"[ERROR] No se pudo descargar el archivo: {response.text}")
        return None
```

## 4. Ejemplo de Uso en el Webhook

```python
@router.post("/webhook")
async def recibir_mensaje(update: TelegramUpdate):
    user_id = update.message.from_.id
    audio = update.message.audio
    voice = update.message.voice
    
    if audio:
        # Archivo de audio
        file_id = audio.file_id
        file_name = audio.file_name
        duration = audio.duration
        
        # Descargar el archivo
        audio_content = download_file(file_id, f"downloads/{file_name}")
        
        logger.info(f"Archivo de audio descargado: {file_name}")
        
    elif voice:
        # Mensaje de voz
        file_id = voice.file_id
        duration = voice.duration
        
        # Descargar el archivo
        voice_content = download_file(file_id, f"downloads/voice_{file_id}.ogg")
        
        logger.info(f"Mensaje de voz descargado: {duration}s")
```

## 5. Flujo Completo

```
1. Usuario envía audio → Telegram
2. Telegram envía webhook con file_id → Tu aplicación
3. Tu aplicación usa file_id para obtener file_path → API de Telegram
4. Tu aplicación construye URL de descarga con file_path
5. Tu aplicación descarga el archivo usando la URL
```

## 6. Consideraciones Importantes

### Límites de Tamaño
- **Archivos de audio**: Hasta 50 MB
- **Mensajes de voz**: Hasta 20 MB

### Duración de los IDs
- Los `file_id` pueden expirar después de un tiempo
- Es recomendable descargar el archivo inmediatamente

### Formato de Archivos
- **Archivos de audio**: MP3, WAV, FLAC, etc.
- **Mensajes de voz**: Siempre OGG

## 7. Ejemplo de Respuesta Completa

```python
# Cuando recibes un audio, el proceso es:
file_id = "CQACAgIAAxkBAAIBY2Q..."

# 1. Obtener información
file_info = get_file_info(file_id)
# Resultado: {"file_path": "voice/file_123.ogg", "file_size": 256000}

# 2. Construir URL
file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/voice/file_123.ogg"

# 3. Descargar
audio_content = requests.get(file_url).content

# 4. Guardar o procesar
with open("audio_recibido.ogg", "wb") as f:
    f.write(audio_content)
```

## Resumen

- **El audio NO llega como URL directa** en el webhook
- **Llega como metadata** con un `file_id`
- **Necesitas hacer 2 peticiones adicionales**:
  1. Obtener `file_path` usando `file_id`
  2. Descargar usando la URL construida con `file_path`
- **El archivo real está en los servidores de Telegram** y se accede mediante la API 