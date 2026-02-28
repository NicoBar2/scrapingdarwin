from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.services.security_service import evaluate_password
from app.utils.response import success_response, error_response
from app.logger_config import logger

security_bp = Blueprint("security", __name__)

@security_bp.route("/security/evaluar-password", methods=["POST"])
@jwt_required()
def evaluar_password():
    
    #region Información API para evaluar la robustez de una contrsaeña
    """
    Evaluar la fortaleza de una contraseña
    ---
    tags:
      - Seguridad
    description: Evalúa una contraseña según longitud, mayúsculas, minúsculas, números y caracteres especiales. Devuelve un puntaje y nivel de seguridad.
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            password:
              type: string
              example: "P@ssw0rd123"
    responses:
      200:
        description: Resultado del análisis de contraseña
        schema:
          type: object
          properties:
            is_success:
              type: boolean
            data:
              type: object
              properties:
                score:
                  type: integer
                nivel:
                  type: string
                  enum: ["débil", "media", "fuerte"]
                detalles:
                  type: object
                  properties:
                    length:
                      type: boolean
                    uppercase:
                      type: boolean
                    lowercase:
                      type: boolean
                    number:
                      type: boolean
                    special:
                      type: boolean
            error_message:
              type: string
      400:
        description: Error de validación del input
      500:
        description: Error interno
    """
    #endregion
    
    try:
        data = request.get_json()

        if not data or "password" not in data:
            logger.warning({
                "event": "evaluar_password_missing_field"
            })
            return error_response("Campo 'password' es requerido", 400)

        password = data["password"]

        if not isinstance(password, str) or not password.strip():
            logger.warning({
                "event": "evaluar_password_invalid_input"
            })
            return error_response("Password inválido", 400)

        result = evaluate_password(password)

        logger.info({
            "event": "evaluar_password_success"
        })

        return success_response(result)

    except Exception as e:
        logger.error({
            "event": "evaluar_password_error",
            "detail": str(e)
        })
        return error_response("Error al evaluar contraseña", 500)