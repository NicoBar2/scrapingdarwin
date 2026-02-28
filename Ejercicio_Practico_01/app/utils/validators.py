import ipaddress
from app.logger_config import logger
from datetime import datetime, timezone

def validate_ip(ip_str: str):
    try:
        if not ip_str:
            logger.warning({
                "event": "ip_empty"
            })
            return False, "La IP no puede estar vacía"

        ip_obj = ipaddress.ip_address(ip_str)

        result = {
            "valid": True,
            "version": f"IPv{ip_obj.version}",
            "private": ip_obj.is_private
        }

        logger.info({
            "event": "ip_validated",
            "ip": ip_str,
            "version": ip_obj.version,
            "private": ip_obj.is_private
        })

        return True, result

    except ValueError:
        logger.warning({
            "event": "ip_invalid_format",
            "ip": ip_str
        })
        return False, "Formato de IP inválido"

    except Exception as e:
        logger.error({
            "event": "ip_validation_error",
            "detail": str(e)
        })
        return False, "Error interno al validar IP"
    
def calculate_age(birthdate_str: str):
    try:
        if not birthdate_str:
            logger.warning({
                "event": "birthdate_empty"
            })
            return False, "La fecha de nacimiento es obligatoria"

        try:
            birthdate = datetime.strptime(
                birthdate_str, "%Y-%m-%d"
            ).replace(tzinfo=timezone.utc)
        except ValueError:
            logger.warning({
                "event": "birthdate_invalid_format",
                "value": birthdate_str
            })
            return False, "Formato inválido. Use YYYY-MM-DD"

        today = datetime.now(timezone.utc)

        if birthdate > today:
            logger.warning({
                "event": "birthdate_future",
                "value": birthdate_str
            })
            return False, "La fecha no puede ser futura"

        years = today.year - birthdate.year
        months = today.month - birthdate.month
        days = today.day - birthdate.day

        if days < 0:
            months -= 1
            previous_month = (today.month - 1) or 12
            previous_year = today.year if today.month != 1 else today.year - 1
            last_day_previous_month = (
                datetime(previous_year, previous_month + 1, 1, tzinfo=timezone.utc)
                - datetime(previous_year, previous_month, 1, tzinfo=timezone.utc)
            ).days
            days += last_day_previous_month

        if months < 0:
            years -= 1
            months += 12

        result = {
            "edad": years,
            "detalle": {
                "anios": years,
                "meses": months,
                "dias": days
            },
            "mayor_edad": years >= 18
        }

        logger.info({
            "event": "age_calculated",
            "birthdate": birthdate_str,
            "age": years
        })

        return True, result

    except Exception as e:
        logger.error({
            "event": "age_calculation_error",
            "detail": str(e)
        })
        return False, "Error interno al calcular edad"
    
def validate_ecuadorian_identification(identification: str):
    try:
        if not identification:
            logger.warning({"event": "cedula_empty"})
            return False, "La cédula es obligatoria"

        if not identification.isdigit():
            logger.warning({
                "event": "cedula_not_numeric",
                "value": identification
            })
            return False, "La cédula debe contener solo números"

        if len(identification) != 10:
            logger.warning({
                "event": "cedula_invalid_length",
                "value": identification
            })
            return False, "La cédula debe tener 10 dígitos"

        provincia = int(identification[:2])
        if provincia < 1 or provincia > 24:
            logger.warning({
                "event": "cedula_invalid_province",
                "province": provincia
            })
            return False, "Código de provincia inválido"

        tercer_digito = int(identification[2])
        if tercer_digito >= 6:
            logger.warning({
                "event": "cedula_invalid_third_digit"
            })
            return False, "Tercer dígito inválido"

        coeficientes = [2,1,2,1,2,1,2,1,2]
        suma = 0

        for i in range(9):
            valor = int(identification[i]) * coeficientes[i]
            if valor > 9:
                valor -= 9
            suma += valor

        digito_verificador = (10 - (suma % 10)) % 10

        if digito_verificador != int(identification[9]):
            logger.warning({
                "event": "cedula_invalid_verifier",
                "value": identification
            })
            return False, "Dígito verificador incorrecto"

        logger.info({
            "event": "cedula_validated",
            "province": provincia
        })

        return True, {
            "valida": True,
            "provincia": provincia
        }

    except Exception as e:
        logger.error({
            "event": "cedula_validation_error",
            "detail": str(e)
        })
        return False, "Error interno al validar cédula"