import base64
import os
import re
from typing import Optional

import pandas as pd
from googleapiclient.discovery import Resource as GoogleResource
from pandas.core.interchange.dataframe_protocol import DataFrame
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.constants import API_DETAILS
from app.db.models import User
from app.utils.handle_file import save_tt
from app.utils.response import APIResponse
from app.settings import Settings
from app.services.google_services import GoogleServices
from  fastapi import  status

from app.utils.logger import logger


class TtAutomation:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.services = GoogleServices(self.settings)
        self.gmail_service:Optional[GoogleResource] = None
        self.calendar_service:Optional[GoogleResource] = None
        self.SCOPE = API_DETAILS["gmail"]["scopes"]+API_DETAILS["calendar"]["scopes"]

    def get_service(self,user_id: str):
        try:
            services_response = self.services.get_service(scope=self.SCOPE, user_id=user_id)
            if services_response.get("code")== status.HTTP_200_OK:
                services = services_response.get("data")
                self.gmail_service = services.get("gmail")
                self.calendar_service = services.get("calendar")
                return APIResponse.success()
            elif services_response.get("code")== status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED:
                logger.warning("Authentication failed, User needs to authenticate")
                return APIResponse.auth_required(redirect_url=services_response.get("data"))
            else:
                logger.error(f"Status code {services_response.get('code')} Message: {services_response.get('message')}")
                return None

        except Exception as e:
            logger.error("Failed to get Google API service with error message: {}".format(e))
            return APIResponse.error(f"Service creation failed: {str(e)}",
                              status.HTTP_500_INTERNAL_SERVER_ERROR)
    def handle_auth_callback(self, code: str,user_id:str )->str:
        return self.services.handle_auth_callback(code=code, scopes=self.SCOPE,user_id=user_id)

    async def get_user_info(self,user_id:str,session:AsyncSession):
        try:
            query = select(User).where(User.username==user_id)
            results = await session.execute(query)
            user = results.scalars().first()

            if user:
                return user.model_dump()
            else:
                logger.debug(f"No user found with username: {user_id}")
                return None
        except Exception as e:
            logger.error("Failed to get user info with error message: {}".format(e))
            return None

    async def save_user_info(self,user:User,session:AsyncSession):
        try:
            session.add(user)
            await session.commit()
            await session.refresh(user)
            logger.debug(f"User {user.username} saved")
            return APIResponse.success()
        except Exception as e:
            logger.error("Failed to save user info with error message: {}".format(e))
            return None

    async def get_attachment(self,user_id:str,msg_id:str,attachment_id:str,user_info:dict):
        try:
            if not self.gmail_service:
                self.gmail_service = self.get_service(user_id=user_id)
            attachment = self.gmail_service.users().messages().attachments().get(
                userId='me',
                messageId=msg_id,
                id=attachment_id
            ).execute()
            file_data = base64.urlsafe_b64decode(attachment['data'])
            saved_file_path = await save_tt(file_data=file_data,user_info=user_info)
            logger.debug(f"Attachment Received")

            return saved_file_path
        except Exception as e:
            logger.error("Failed to get emails from Google API service with error message: {}".format(e))
            return None
    def get_schedule(self,file_name_og:str,user_info:dict):
        file_name = f"{user_info.get('department')}_{user_info.get('div')}_{user_info.get('year')}_att-{user_info.get("file_name_og")}"
        saved_files = os.listdir("attachments")
        logger.debug(f"Saved files: {saved_files}")
        for file in saved_files:
            cleaned_name = re.sub(r"date-\d{8}-\d{6}_", "", file)
            logger.debug(f"Cleaned name: {cleaned_name}")
            if cleaned_name == file_name:
                logger.info(f"File {file_name} found")
                return os.path.join("attachments", file)
        logger.info(f"File {file_name} not found")
        return None
