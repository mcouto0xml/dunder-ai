import os
import time
import requests 
import pygame

API_KEY = "8963349fe4e198d90e89d25007e9805ca4862675d840a70fddac5221e936d9f0"

VOICE_ID = "vxXIz4jd885iK3G3bqGP" 

def falar_texto(texto: str):
    """
    Gera áudio usando API direta do ElevenLabs e toca com Pygame.
    """
    if not texto:
        return

    print(f"🔊 Michael Scott está falando: '{texto[:50]}...'")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": API_KEY
    }

    data = {
        "text": texto,
        "model_id": "eleven_multilingual_v2", 
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    arquivo_temp = "temp_michael.mp3"

    try:
        response = requests.post(url, json=data, headers=headers)

        if response.status_code != 200:
            print(f"Erro na API ElevenLabs ({response.status_code}): {response.text}")
            return

        with open(arquivo_temp, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        
        pygame.mixer.init()
        pygame.mixer.music.load(arquivo_temp)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
            
        pygame.mixer.music.unload()
        pygame.mixer.quit()

        try:
            os.remove(arquivo_temp)
        except:
            pass

    except Exception as e:
        print(f"Erro crítico no áudio: {e}")

if __name__ == "__main__":
    falar_texto("Toby, you are not a real person. I am sure about it.")