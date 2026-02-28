import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:

    # ==========================
    # JWT CONFIG (mínimo necesario)
    # ==========================
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 3600)))

    # ==========================
    # EXTERNAL APIs
    # ==========================
    IP_GEO_URL = os.getenv("IP_GEO_URL")
    GENDERIZE_URL = os.getenv("GENDERIZE_URL")
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 5))
    
    # ==========================
    # CREDENCIALES DE USUARIO
    # ==========================
    AUTH_USERNAME = os.getenv("AUTH_USERNAME")
    AUTH_PASSWORD = os.getenv("AUTH_PASSWORD")

    # ===========================
    # CONFIGURACIÓN SERVIDOR SMTP
    # ===========================
    SMTP_SERVER = "smtp.office365.com"
    SMTP_PORT = 587
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    
    # ============================
    # CREDENCIALES DE GOOGLE CLOUD
    # ============================
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")