from flask import Blueprint, request, current_app
from flask_jwt_extended import create_access_token
from app.utils.response import success_response, error_response
from app.services.auth_service import register_user_service
from app.logger_config import logger

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/auth/login", methods=["POST"])
def login():
    
    #region Información API Autenticación de usuario
    """
    Autenticación de usuario
    ---
    tags:
      - Auth
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
            - username
            - password
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      200:
        description: Usuario autenticado exitosamente
    """
    #endregion

    try:
        data = request.get_json()

        if not data:
            logger.warning({"event": "login_no_payload"})
            return error_response("No se enviado información", 400)

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            logger.warning({
                "event": "login_missing_fields",
                "username": username
            })
            return error_response("Usuario y contraseña son obligatorios", 400)

        env_username = current_app.config["AUTH_USERNAME"]
        env_password = current_app.config["AUTH_PASSWORD"]

        if username != env_username or password != env_password:
            logger.warning({
                "event": "login_invalid_credentials",
                "username": username
            })
            return error_response("Credenciales inválidas", 401)

        access_token = create_access_token(identity=username)

        logger.info({
            "event": "login_success",
            "username": username
        })

        return success_response({
            "access_token": access_token
        })

    except Exception as e:
        logger.error({
            "event": "login_error",
            "detail": str(e)
        })
        return error_response("Error interno en autenticación", 500)
    
@auth_bp.route("/auth/register", methods=["POST"])
def register():
    
    #region Información API Registro usuario
    """
    Registrar nuevo usuario
    ---
    tags:
      - Auth
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
            - identification
            - name
            - last_name
            - username
            - email
            - password
          properties:
            identification:
              type: string
            name:
              type: string
            last_name:
              type: string
            username:
              type: string
            email:
              type: string
            password:
              type: string
    responses:
      200:
        description: Usuario registrado correctamente
    """
    #endregion
    
    try:
        data = request.get_json()

        required_fields = ["identification", "name", "last_name", "username", "email", "password"]

        if not data or not all(field in data for field in required_fields):
            return error_response("Todos los campos son requeridos", 400)

        success, result = register_user_service(data)

        if not success:
            return error_response(result, 400)

        logger.info({
            "event": "user_registered",
            "email": data["email"]
        })

        return success_response(result)

    except Exception as e:
        logger.error({
            "event": "register_controller_error",
            "detail": str(e)
        })
        return error_response("Error interno en auth", 500)