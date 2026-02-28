import time
from flask import request
from app.logger_config import logger

def register_request_logging(app):

    @app.before_request
    def start_timer():
        request.start_time = time.time()

    @app.after_request
    def log_request(response):
        duration = round((time.time() - request.start_time) * 1000, 2)

        logger.info({
            "endpoint": request.path,
            "method": request.method,
            "status_code": response.status_code,
            "response_time_ms": duration,
            "client_ip": request.remote_addr
        })

        return response