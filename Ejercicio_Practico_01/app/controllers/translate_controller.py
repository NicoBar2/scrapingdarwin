from flask_jwt_extended import jwt_required
from flask import Blueprint, request
from app.services.translate_service import translate_text
from app.logger_config import logger
from app.utils.response import success_response, error_response

translate_bp = Blueprint("translate", __name__)

@translate_bp.route("/translate", methods=["POST"])
@jwt_required()
def translate_endpoint():
    
    """
    Traduce un texto a un idioma destino usando Google Translate API.
    ---
    tags:
      - Traducción
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        description: JSON con el texto a traducir y el idioma destino
        schema:
          type: object
          required:
            - text
          properties:
            text:
              type: string
              description: Texto que se desea traducir
              example: "Hola mundo"
            target_language:
              type: string
              description: Código ISO 639-1 del idioma destino
              example: "en"
    responses:
      200:
        description: Traducción exitosa
      400:
        description: Error de validación
      401:
        description: Token inválido o faltante
      500:
        description: Error interno del servidor
    """
    
    try:
        data = request.get_json(silent=True) or {}

        text = data.get("text")
        target = data.get("target_language", "en")

        # Validaciones
        if not isinstance(text, str) or not text.strip():
            logger.warning({"event": "translate_validation", "detail": "text requerido", "payload": data})
            return error_response("Campo 'text' es requerido", 400)

        if not isinstance(target, str) or len(target.strip()) != 2:
            logger.warning({"event": "translate_validation", "detail": "target_language inválido", "payload": data})
            return error_response("Campo 'target_language' debe ser ISO 639-1 (ej: 'en')", 400)

        result = translate_text(text.strip(), target.strip())

        if not isinstance(result, dict):
            logger.error({"event": "translate_service_contract_error", "detail": "translate_text no devolvió dict"})
            return error_response("Error interno en translate", 500)

        if not result.get("success"):
            logger.error({"event": "translate_service_failed", "detail": result.get("error"), "payload": data})
            return error_response(result.get("error", "Error traduciendo"), 500)

        payload = {
            "original": result.get("original"),
            "translated": result.get("translated"),
            "target_language": result.get("target_language", target.strip()),
        }

        logger.info({"event": "translate_success", "target_language": payload["target_language"]})
        return success_response(payload)  # (json, 200) si tu helper lo hace así

    except Exception as e:
        logger.exception({"event": "translate_controller_error", "detail": str(e)})
        return error_response("Error interno en translate", 500)