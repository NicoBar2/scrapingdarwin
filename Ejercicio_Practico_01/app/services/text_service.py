import re
import unicodedata
from app.logger_config import logger


def normalizar_texto(texto: str):
    try:
        if texto is None:
            return False, "El texto no puede ser nulo"

        if not isinstance(texto, str):
            return False, "El texto debe ser una cadena"

        original = texto

        # Quitar espacios al inicio y final
        texto = texto.strip()

        if texto == "":
            return False, "El texto no puede estar vacío"

        # Quitar tildes
        texto = unicodedata.normalize("NFD", texto)
        texto = texto.encode("ascii", "ignore").decode("utf-8")

        # Pasar a mayúsculas
        texto = texto.upper()

        # Quitar espacios múltiples
        texto = re.sub(r"\s+", " ", texto)

        return True, {
            "original": original,
            "normalizado": texto
        }

    except Exception as e:
        logger.error({
            "event": "normalizar_texto_error",
            "detail": str(e)
        })
        return False, "Error interno al normalizar texto"


def limpiar_caracteres(texto: str):
    try:
        if texto is None:
            return False, "El texto no puede ser nulo"

        if not isinstance(texto, str):
            return False, "El texto debe ser una cadena"

        if texto.strip() == "":
            return False, "El texto no puede estar vacío"

        # Permitir solo letras y números
        limpio = re.sub(r"[^a-zA-Z0-9\s]", "", texto)

        return True, {
            "original": texto,
            "limpio": limpio.upper()
        }

    except Exception as e:
        logger.error({
            "event": "limpiar_caracteres_error",
            "detail": str(e)
        })
        return False, "Error interno al limpiar caracteres"