import os
import requests
from dotenv import load_dotenv
from app.logger_config import logger

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

def translate_text(text: str, target_lang: str = "en") -> dict:
    try:
        logger.info(f"[TRANSLATE] Iniciando traducción -> target={target_lang}")

        if not API_KEY:
            logger.error("[TRANSLATE] GOOGLE_API_KEY no configurada")
            return {
                "success": False,
                "error": "API key not configured"
            }

        if not text:
            logger.warning("[TRANSLATE] Texto vacío recibido")
            return {
                "success": False,
                "error": "Text cannot be empty"
            }

        url = "https://translation.googleapis.com/language/translate/v2"

        params = {
            "q": text,
            "target": target_lang,
            "key": API_KEY
        }

        response = requests.post(url, params=params, timeout=10)

        logger.debug(f"[TRANSLATE] Status code: {response.status_code}")

        if response.status_code != 200:
            logger.error(f"[TRANSLATE] Error HTTP: {response.text}")
            return {
                "success": False,
                "error": "Translation API error",
                "details": response.text
            }

        data = response.json()

        translated_text = data["data"]["translations"][0]["translatedText"]

        logger.info("[TRANSLATE] Traducción exitosa")

        return {
            "success": True,
            "original": text,
            "translated": translated_text,
            "target_language": target_lang,
        }

    except requests.exceptions.Timeout:
        logger.error("[TRANSLATE] Timeout al conectar con Google API")
        return {
            "success": False,
            "error": "Translation service timeout"
        }

    except Exception as e:
        logger.exception(f"[TRANSLATE] Error inesperado: {e}")
        return {
            "success": False,
            "error": "Unexpected error occurred"
        }