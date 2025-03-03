from typing import Optional, Dict, Any, List
from app.constants import API_DETAILS
from app.response import APIResponse
from app.settings import Settings
from app.services.google_services import GoogleServices
from  fastapi import  status

class TtAutomation:
    def __init__(self, settings: Settings, user_id: str):
        """Initialize Google Services for Gmail and Calendar."""
        self.settings = settings
        self.services = GoogleServices(self.settings)
        self.gmail_service = None
        self.calendar_service = None
        self.SCOPE = API_DETAILS["gmail"]["scopes"]+API_DETAILS["calendar"]["scopes"]
        self.user_id = user_id or "default"

    def get_service(self):
        try:
            services = self.services.get_service(scope=self.SCOPE, user_id=self.user_id)
            if services.get("code")== status.HTTP_200_OK:
                self.gmail_service = services.get("gmail")
                self.calendar_service = services.get("calendar")
                return APIResponse.success(services)
            elif services.get("code")== status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED:
                print("Authentication required")
                return APIResponse.auth_required(redirect_url=services.get("data"))
            else:
                print(f"Something went wrong: Status code {services.get('code')} Message: {services.get('message')}")
                return None

        except Exception as e:
            return APIResponse.error(f"Service creation failed: {str(e)}",
                              status.HTTP_500_INTERNAL_SERVER_ERROR)
    def handle_auth_callback(self, code: str )->str:
        return self.services.handle_auth_callback(code=code, scopes=self.SCOPE,user_id=self.user_id)
