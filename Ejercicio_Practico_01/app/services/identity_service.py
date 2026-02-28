import requests
from decimal import Decimal, InvalidOperation
from requests.exceptions import RequestException, Timeout
from app.config import Config
from app.logger_config import logger
from num2words import num2words
from app.utils.validators import (calculate_age,validate_ecuadorian_identification)


# ==============================
# VERIFICAR CÉDULA
# ==============================

def verificar_cedula(cedula: str):
    return validate_ecuadorian_identification(cedula)


# ==============================
# CALCULAR EDAD
# ==============================

def obtener_edad(fecha_nacimiento: str):
    return calculate_age(fecha_nacimiento)


# ==============================
# CONVERTIR NÚMERO A LETRAS
# ==============================
def numero_a_letras_moneda(numero):
    try:
        # Validar que no venga vacío
        if numero is None:
            return {
                "success": False,
                "error": "El valor no puede ser nulo"
            }

        # Convertir a Decimal para evitar problemas de float
        try:
            numero_decimal = Decimal(str(numero))
        except InvalidOperation:
            return {
                "success": False,
                "error": "El valor debe ser numérico"
            }

        # Validar negativo
        if numero_decimal < 0:
            return {
                "success": False,
                "error": "El monto no puede ser negativo"
            }

        # Conversión a letras
        letras = num2words(
            numero_decimal,
            lang='es',
            to='currency',
            currency='USD'
        )

        return {
            "success": True,
            "numero": float(numero_decimal),
            "en_letras": letras.upper()
        }

    except ValueError as e:
        logger.error({
            "evento": "numero_a_letras_value_error",
            "numero": numero,
            "detalle": str(e)
        })
        return {
            "success": False,
            "error": "Error en el formato del número"
        }

    except Exception as e:
        logger.error({
            "evento": "numero_a_letras_error",
            "numero": numero,
            "detalle": str(e)
        })
        return {
            "success": False,
            "error": "Error interno al convertir el número a letras"
        }

# ==============================
# GÉNERO (API EXTERNA)
# ==============================

def obtener_genero(nombre: str):
    try:
        response = requests.get(
            Config.GENDERIZE_URL,
            params={"name": nombre},
            timeout=Config.REQUEST_TIMEOUT
        )

        response.raise_for_status()
        data = response.json()

    except Timeout:
        logger.error({
            "evento": "gender_timeout",
            "nombre": nombre
        })
        return {"error": "El servicio de género tardó demasiado en responder"}

    except RequestException as e:
        logger.error({
            "evento": "gender_request_error",
            "nombre": nombre,
            "detalle": str(e)
        })
        return {"error": "Error al consultar servicio de género"}

    # Transformar respuesta (no devolver crudo)
    return {
        "nombre": data.get("name"),
        "genero": data.get("gender"),
        "probabilidad": data.get("probability"),
        "cantidad_registros": data.get("count")
    }