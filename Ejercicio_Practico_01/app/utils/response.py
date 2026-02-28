def success_response(data=None):
    return {
        "is_success": True,
        "data": data,
        "error_message": None
    }

def error_response(message,error_code):
    return {
        "is_success": False,
        "data": None,
        "error_message": message,
        "error_code":error_code
    }