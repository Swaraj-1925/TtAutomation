import os
from fastapi import status, Depends
from googleapiclient.discovery import build, Resource
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from typing import List, Optional, Dict

from app.response import APIResponse
from app.settings import Settings


class GoogleServices:
    def __init__(self, cfg: Settings):
        self.cfg = cfg
        self._create_dir("tokens")
        self.redirect_uri = self.cfg.REDIRECT_URI

    def _create_dir(self, dir_name: str):
        os.makedirs(dir_name, exist_ok=True)

    def _saved_tokens(self, scopes: List[str], token_file_path: str) -> Optional[Dict[str, Resource]]:
        creds = None
        if os.path.exists(token_file_path):
            creds = Credentials.from_authorized_user_file(token_file_path, scopes)

        if creds and creds.valid:
            gmail_service = build("gmail", "v1", credentials=creds)
            calendar_service = build("calendar", "v3", credentials=creds)
            return {"gmail": gmail_service, "calendar": calendar_service}

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(GoogleRequest())
            with open(token_file_path, "w") as token:
                token.write(creds.to_json())
            gmail_service = build("gmail", "v1", credentials=creds)
            calendar_service = build("calendar", "v3", credentials=creds)
            return {"gmail": gmail_service, "calendar": calendar_service}

        return None

    def _get_auth_url(self, scopes:List[str],state: str = None) -> str:
        flow = Flow.from_client_secrets_file(
            self.cfg.GOOGLE_CLIENT_SECRET_FILE,
            scopes=scopes,
            redirect_uri=self.redirect_uri  # Added redirect_uri here
        )
        auth_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent',
            state=state
        )
        # Save state somewhere (session, db, etc.) to verify in callback
        # self.save_state(state)
        return auth_url

    def get_service(self,scope:List[str],user_id:str):
        token_file_path= os.path.join("tokens", f"{user_id}.json")
        print(token_file_path)
        try:
            services = self._saved_tokens(scope, token_file_path)
            print(services)
            if services:
                return APIResponse.success(services)
            else:
                auth_url = self._get_auth_url(scope,state=user_id)
                return APIResponse.auth_required(redirect_url=auth_url)

        except Exception as e:
            print(f"Failed to create Google API service with error message: \n", e)
            if os.path.exists(token_file_path):
                os.remove(token_file_path)
            return APIResponse.error("Unable to create Google API service", status.HTTP_401_UNAUTHORIZED)

    def handle_auth_callback(self, code: str, scopes: List[str], user_id: str = "Token") -> str:
        token_file_path = os.path.join("tokens", f"{user_id}.json")
        flow = Flow.from_client_secrets_file(
            self.cfg.GOOGLE_CLIENT_SECRET_FILE,
            scopes=scopes,
            redirect_uri=self.redirect_uri
        )
        flow.fetch_token(code=code)
        creds = flow.credentials
        with open(token_file_path, "w") as token:
            token.write(creds.to_json())
        return user_id