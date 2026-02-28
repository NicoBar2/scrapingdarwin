from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.services.text_service import normalizar_texto, limpiar_caracteres
from app.utils.response import success_response, error_response
from app.logger_config import logger

text_bp = Blueprint("text", __name__)

@text_bp.route("/text/normalizar", methods=["POST"])
@jwt_required()
def normalizar():
    
    #region Información API para limpiar un texto
    """
    Normalizar información ingresada y convertir en mayúsculas
    ---
    tags:
      - Text
    security:
      - Bearer: []
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - texto
          properties:
            texto:
              type: string
              example: "TraTamiEnto De DaTos"
    responses:
      200:
        description: Texto normalizado correctamente
      400:
        description: Error de validación
      401:
        description: Token inválido o faltante
    """
    #endregion
    
    
    try:
        data = request.get_json()

        if not data or "texto" not in data:
            return error_response("Campo 'texto' es requerido", 400)

        texto = data["texto"]

        success, result = normalizar_texto(texto)

        if not success:
            return error_response(result, 400)

        logger.info({"event": "normalizar_texto_success"})

        return success_response(result)

    except Exception as e:
        logger.error({
            "event": "normalizar_texto_controller_error",
            "detail": str(e)
        })
        return error_response("Error interno en text", 500)

@text_bp.route("/text/limpiar", methods=["POST"])
@jwt_required()
def limpiar():
    
    #region Información API para limpiar un texto
    """
    Limpiar texto de caracteres especiales
    ---
    tags:
      - Text
    security:
      - Bearer: []
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - texto
          properties:
            texto:
              type: string
              example: "Tra##T#am*iEnto De D!$atO$$$S"
    responses:
      200:
        description: Texto limpiado correctamente
      400:
        description: Error de validación
      401:
        description: Token inválido o faltante
    """
    #endregion
    
    try:
        data = request.get_json()

        if not data or "texto" not in data:
            return error_response("Campo 'texto' es requerido", 400)

        texto = data["texto"]

        success, result = limpiar_caracteres(texto)

        if not success:
            return error_response(result, 400)

        logger.info({"event": "limpiar_texto_success"})

        return success_response(result)

    except Exception as e:
        logger.error({
            "event": "limpiar_texto_controller_error",
            "detail": str(e)
        })
        return error_response("Error interno en text", 500)