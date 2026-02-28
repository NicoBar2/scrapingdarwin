from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.utils.response import success_response, error_response
from app.services.identity_service import (
    verificar_cedula,
    obtener_edad,
    numero_a_letras_moneda,
    obtener_genero
)
from app.logger_config import logger

identity_bp = Blueprint("identity", __name__)

@identity_bp.route("/identity/numero-letras", methods=["POST"])
@jwt_required()
def numero_letras():
    
    #region Información API de conversión de números a letras
    """
    Convertir número a letras
    ---
    tags:
      - Utilitarios
    description: Convierte un número a su representación en letras en español con formato de moneda
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            numero:
              type: number
              example: 123.45
    responses:
      200:
        description: Número convertido correctamente
        schema:
          type: object
          properties:
            is_success:
              type: boolean
            data:
              type: object
              properties:
                resultado:
                  type: string
            error_message:
              type: string
      400:
        description: Error de validación
      500:
        description: Error interno
    """
    #endregion
    
    try:
        data = request.get_json()

        if not data or "numero" not in data:
            return error_response("Campo 'numero' es requerido", 400)

        numero = data["numero"]

        result = numero_a_letras_moneda(numero)

        logger.info({"event": "numero_letras_success", "numero": numero})

        return success_response({"resultado": result})

    except Exception as e:
        logger.error({"event": "numero_letras_error", "detail": str(e)})
        return error_response("Error al convertir número", 500)

@identity_bp.route("/identity/verificar-cedula", methods=["POST"])
@jwt_required()
def validar_cedula():
    
    #region Información para validar un número de cédula
    """
    Validar cédula ecuatoriana
    ---
    tags:
    - Utilitarios
    description: Valida una cédula ecuatoriana verificando estructura, dígito verificador y provincia
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            numero:
              type: cedula
              example: 9999999999
    responses:
        200:
            description: Resultado de la validación
            schema:
            type: object
            properties:
                is_success:
                type: boolean
                data:
                type: object
                properties:
                    valida:
                    type: boolean
                    mensaje:
                    type: string
                    provincia:
                    type: string
                error_message:
                type: string
        400:
            description: Cédula inválida
        500:
            description: Error interno
    """
    #endregion
    
    try:
        data = request.get_json()

        if not data or "cedula" not in data:
            return error_response("Campo 'cedula' es requerido", 400)

        cedula = data["cedula"]

        result = verificar_cedula(cedula)

        logger.info({"event": "verificar_cedula", "cedula": cedula})

        return success_response(result)

    except Exception as e:
        logger.error({"event": "verificar_cedula_error", "detail": str(e)})
        return error_response("Error al verificar cédula", 500)

@identity_bp.route("/identity/calcular-edad", methods=["POST"])
@jwt_required()
def edad():
    
    #region Información de API para calcular edad
    """
    Calcular edad a partir de fecha de nacimiento
    ---
    tags:
      - Utilitarios
    description: Devuelve la edad, desglose en años, meses y días y si es mayor de edad
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            fecha_nacimiento:
              type: string
              format: date
              example: "2000-05-15"
    responses:
      200:
        description: Edad calculada correctamente
        schema:
          type: object
          properties:
            is_success:
              type: boolean
            data:
              type: object
              properties:
                edad:
                  type: integer
                detalle:
                  type: object
                  properties:
                    anios:
                      type: integer
                    meses:
                      type: integer
                    dias:
                      type: integer
                mayor_edad:
                  type: boolean
            error_message:
              type: string
      400:
        description: Error de validación
      500:
        description: Error interno
    """
    #endregion
    
    try:
        data = request.get_json()

        if not data or "fecha_nacimiento" not in data:
            return error_response("Campo 'fecha_nacimiento' es requerido", 400)

        fecha = data["fecha_nacimiento"]

        result = obtener_edad(fecha)

        logger.info({"event": "calcular_edad", "fecha": fecha})

        return success_response({"edad": result})

    except Exception as e:
        logger.error({"event": "calcular_edad_error", "detail": str(e)})
        return error_response("Error al calcular edad", 500)

@identity_bp.route("/identity/genero", methods=["POST"])
@jwt_required()
def genero():
    
    #region Información API para obtener el género a partir del nombre
    """
    Predecir género a partir de un nombre
    ---
    tags:
      - Utilitarios
    description: Predice el género (masculino/femenino) basado en un nombre utilizando genderize.io
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            nombre:
              type: string
              example: "Juan"
    responses:
      200:
        description: Género predicho correctamente
        schema:
          type: object
          properties:
            is_success:
              type: boolean
            data:
              type: object
              properties:
                genero:
                  type: string
                probabilidad:
                  type: number
            error_message:
              type: string
      400:
        description: Nombre inválido
      500:
        description: Error interno
    """
    #endregion
    
    try:
        data = request.get_json()

        if not data or "nombre" not in data:
            return error_response("Campo 'nombre' es requerido", 400)

        nombre = data["nombre"]

        result = obtener_genero(nombre)

        logger.info({"event": "genero_success", "nombre": nombre})

        return success_response(result)

    except Exception as e:
        logger.error({"event": "genero_error", "detail": str(e)})
        return error_response("Error al predecir género", 500)