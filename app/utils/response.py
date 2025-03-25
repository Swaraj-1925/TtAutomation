from typing import Any, Optional, Dict
from fastapi import status

class APIResponse:
    @staticmethod
    def success(data: Any = None, status_code: int = status.HTTP_200_OK) -> Dict[str, Any]:
        """Return a successful response."""
        response = {
            "code": status_code,
            "status": "success"
        }
        if data is not None:
            response["data"] = data
        return response

    @staticmethod
    def error(message: str, status_code: int = status.HTTP_400_BAD_REQUEST,
             data: Any = None) -> Dict[str, Any]:
        """Return an error response."""
        response = {
            "code": status_code,
            "status": "error",
            "error": message
        }
        if data is not None:
            response["data"] = data
        return response

    @staticmethod
    def auth_required(redirect_url: str,
                     message: str = "Authorization Required, No valid credentials found") -> Dict[str, Any]:
        """Return an authentication required response."""
        return {
            "code": status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED,
            "status": "auth_required",
            "data": redirect_url,
            "message": message
        }