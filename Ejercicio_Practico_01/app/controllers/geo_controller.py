from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.utils.validators import validate_ip
from app.services.geo_service import get_geo_info
from app.utils.response import success_response, error_response
from app.logger_config import logger

geo_bp = Blueprint("geo", __name__)

@geo_bp.route("/geo/validar-ip", methods=["POST"])
@jwt_required()
def validar_ip():
    
    #region Información API para validar una dirección IP
    """
    Validar IP
    ---
    tags:
      - Geolocalización
    description: Valida si una IP es correcta y si es pública o privada
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            ip:
              type: string
              example: "8.8.8.8"
    responses:
      200:
        description: IP válida
        schema:
          type: object
          properties:
            is_success:
              type: boolean
            data:
              type: object
              properties:
                valid:
                  type: boolean
                version:
                  type: string
                private:
                  type: boolean
            error_message:
              type: string
      400:
        description: Error de validación
      500:
        description: Error interno del servidor
    """
    #endregion
    
    try:
        data = request.get_json()

        if not data or "ip" not in data:
            return error_response("Campo 'ip' es requerido", 400)

        ip = data["ip"]

        success, result = validate_ip(ip)

        if not success:
            return error_response(result, 400)

        return success_response(result)

    except Exception as e:
        logger.error({
            "event": "validar_ip_error",
            "detail": str(e)
        })
        return error_response("Error interno al validar IP", 500)

@geo_bp.route("/geo/localizar-ip", methods=["POST"])
@jwt_required()
def localizar_ip():
    
    #region Información API para geolocalizar dirección IP
    """
    Localizar IP
    ---
    tags:
      - Geolocalización
    description: Devuelve la ubicación geográfica de una IP pública
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            ip:
              type: string
              example: "8.8.8.8"
    responses:
      200:
        description: Información geográfica de la IP
        schema:
          type: object
          properties:
            is_success:
              type: boolean
            data:
              type: object
              properties:
                pais:
                  type: string
                region:
                  type: string
                ciudad:
                  type: string
                lat:
                  type: number
                lon:
                  type: number
            error_message:
              type: string
      400:
        description: IP inválida
      500:
        description: Error interno del servidor
    """
    #endregion
    
    try:
        data = request.get_json()

        if not data or "ip" not in data:
            logger.warning({"event": "localizar_ip_missing_field"})
            return error_response("Campo 'ip' es requerido", 400)

        ip = data["ip"]

        success, validation = validate_ip(ip)

        if not success:
            logger.warning({
                "event": "localizar_ip_invalid",
                "ip": ip
            })
            return error_response(validation, 400)

        if validation["private"]:
            logger.info({
                "event": "localizar_ip_private",
                "ip": ip
            })
            return success_response({
                "mensaje": "IP privada"
            })

        geo = get_geo_info(ip)

        logger.info({
            "event": "localizar_ip_success",
            "ip": ip
        })

        return success_response(geo)

    except Exception as e:
        logger.error({
            "event": "localizar_ip_error",
            "detail": str(e)
        })
        return error_response("Error interno al localizar IP", 500)