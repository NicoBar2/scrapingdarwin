import re
from app.logger_config import logger


def evaluate_password(password: str):
    try:
        #Verificamos si llega la contraseña
        if not password:
            logger.warning({
                "event": "password_empty",
                "message": "Contraseña vacía o nula"
            })

            return False, "La contraseña no puede estar vacía"

        score = 0
        details = {
            "length": False,
            "uppercase": False,
            "lowercase": False,
            "number": False,
            "special": False
        }

        # Longitud mínima 8 caracteres
        if len(password) >= 8:
            score += 20
            details["length"] = True

        # Mayúsculas
        if re.search(r"[A-Z]", password):
            score += 20
            details["uppercase"] = True

        # Minúsculas
        if re.search(r"[a-z]", password):
            score += 20
            details["lowercase"] = True

        # Números
        if re.search(r"\d", password):
            score += 20
            details["number"] = True

        # Caracteres especiales
        if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            score += 20
            details["special"] = True

        # Nivel
        level = "débil"

        if score >= 80:
            level = "fuerte"
        elif score >= 60:
            level = "media"

        result = {
            "score": score,
            "nivel": level,
            "detalles": details
        }

        logger.info({
            "event": "password_evaluated",
            "score": score,
            "level": level
        })

        return True, result

    except Exception as e:
        logger.error({
            "event": "password_evaluation_error",
            "detail": str(e)
        })

        return False, "Error interno al evaluar contraseña"