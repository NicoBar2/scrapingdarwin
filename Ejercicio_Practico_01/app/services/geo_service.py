import requests
from requests.exceptions import Timeout, ConnectionError, HTTPError, RequestException
from app.config import Config
from app.logger_config import logger


def get_geo_info(ip: str):
    try:
        response = requests.get(f"{Config.IP_GEO_URL}/{ip}",timeout=Config.REQUEST_TIMEOUT)

        # Verificar status HTTP
        response.raise_for_status()
        data = response.json()

    except Timeout:
        logger.error({
            "evento": "geo_timeout",
            "ip": ip,
            "mensaje": "Timeout al consultar servicio externo"
        })
        return {"error": "El servicio de geolocalización tardó demasiado en responder"}

    except ConnectionError:
        logger.error({
            "evento": "geo_connection_error",
            "ip": ip,
            "mensaje": "Error de conexión con servicio externo"
        })
        return {"error": "No se pudo conectar con el servicio de geolocalización"}

    except HTTPError as e:
        logger.error({
            "evento": "geo_http_error",
            "ip": ip,
            "status_code": response.status_code,
            "detalle": str(e)
        })
        return {"error": "Error en el servicio externo de geolocalización"}

    except ValueError:
        logger.error({
            "evento": "geo_json_error",
            "ip": ip,
            "mensaje": "Respuesta inválida (no es JSON)"
        })
        return {"error": "Respuesta inválida del servicio externo"}

    except RequestException as e:
        logger.error({
            "evento": "geo_request_exception",
            "ip": ip,
            "detalle": str(e)
        })
        return {"error": "Error inesperado al consultar geolocalización"}

    # Validar estructura esperada
    if not data.get("success", False):
        logger.warning({
            "evento": "geo_api_failure",
            "ip": ip,
            "respuesta": data
        })
        return {"error": "No se pudo obtener información de la IP"}

    # Transformar respuesta (no exponer crudo)
    return {
        "pais": data.get("country"),
        "region": data.get("region"),
        "ciudad": data.get("city"),
        "latitud": data.get("latitude"),
        "longitud": data.get("longitude"),
        "timezone": data.get("timezone", {}).get("id")
    }