from flask import Flask
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from app.config import Config
from app.middleware.request_logger import register_request_logging

from app.controllers.auth_controller import auth_bp
from app.controllers.geo_controller import geo_bp
from app.controllers.identity_controller import identity_bp
from app.controllers.security_controller import security_bp
from app.controllers.text_controller import text_bp
from app.controllers.translate_controller import translate_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # JWT
    JWTManager(app)

    # Middleware logging
    register_request_logging(app)

    # Blueprints con prefijo /api
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(geo_bp, url_prefix="/api")
    app.register_blueprint(identity_bp, url_prefix="/api")
    app.register_blueprint(security_bp, url_prefix="/api")
    app.register_blueprint(text_bp, url_prefix="/api")
    app.register_blueprint(translate_bp, url_prefix="/api")

    # 🔥 Swagger Config
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "API - Ejercicio Práctico",
            "description": "Documentación técnica de las API generadas para sanitizar y validar información",
            "version": "1.0"
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "Ejemplo: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    }

    swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/api/docs/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "swagger_ui": True,
    "specs_route": "/api/docs/",
    "static_url_path": "/api/docs/flasgger_static"
    }

    Swagger(app, template=swagger_template, config=swagger_config)
    
    return app