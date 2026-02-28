import smtplib
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.config import Config
from app.logger_config import logger


def register_user_service(data):

    try:
        email = data["email"]

        # Generar token ficticio
        reset_token = str(uuid.uuid4())

        # URL ficticia
        reset_url = f"https://mcib_tratamientodatos_2026.com/reset-password/{reset_token}"

        send_registration_email(email, data["name"], data["last_name"], reset_url)

        return True, {
            "message": "Usuario registrado exitosamente. Revise su correo.",
            "reset_password_url": reset_url
        }

    except Exception as e:
        logger.error({
            "event": "register_service_error",
            "detail": str(e)
        })
        return False, "Error al registrar usuario"


def send_registration_email(to_email, name, last_name, reset_url):

    msg = MIMEMultipart()
    msg["From"] = Config.SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = "Registro exitoso"

    body = f"""
    Hola {name} {last_name},

    Su usuario ha sido registrado exitosamente.

    Por seguridad debe cambiar su contraseña en el siguiente enlace:

    {reset_url}

    Saludos.
    """

    msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT)
    server.starttls()
    server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
    server.send_message(msg)
    server.quit()

    logger.info({
        "event": "registration_email_sent",
        "email": to_email
    })