import base64
import os
import re
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
from googleapiclient.discovery import Resource as GoogleResource, Resource
from pandas.core.interchange.dataframe_protocol import DataFrame
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.constants import API_DETAILS, CREATOR_EMAIL, TAG
from app.db.models import User
from app.services.calendar import get_next_weekday, create_event
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
                logger.error("Authentication failed, User needs to authenticate")
                return APIResponse.auth_required(redirect_url=services_response.get("data"))
            else:
                logger.critical(f"Status code {services_response.get('code')} Message: {services_response.get('message')}")
                return None

        except Exception as e:
            logger.critical("Failed to get Google API service with error message: {}".format(e))
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
                return APIResponse.success(user.model_dump())
            else:
                logger.debug(f"No user found with username: {user_id}")
                return APIResponse.error(f"No user found with username: {user_id}")
        except Exception as e:
            logger.error("Failed to get user info with error message: {}".format(e))
            return APIResponse.error(f"Failed to get user info with error message: {str(e)}",)

    async def save_user_info(self,user:User,session:AsyncSession):
        try:
            session.add(user)
            await session.commit()
            await session.refresh(user)
            logger.debug(f"User {user.username} saved")
            return APIResponse.success()
        except Exception as e:
            logger.error("Failed to save user info with error message: {}".format(e))
            return APIResponse.error(f"Failed to save user info with error message: {str(e)}",)

    async def get_attachment(self,user_id:str,msg_id:str,attachment_id:str,user_info:dict):
        try:
            if not self.gmail_service:
                self.get_service(user_id=user_id)
            attachment = self.gmail_service.users().messages().attachments().get(
                userId='me',
                messageId=msg_id,
                id=attachment_id
            ).execute()
            file_data = base64.urlsafe_b64decode(attachment['data'])
            saved_file_path = await save_tt(file_data=file_data,user_info=user_info)
            logger.debug(f"Attachment Received")

            return APIResponse.success(saved_file_path)
        except Exception as e:
            logger.error("Failed to get emails from Google API service with error message: {}".format(e))
            return APIResponse.error(f"Failed to get emails from Google API service with error message: {e}",)
    def get_schedule(self,user_info:dict):
        try:
            file_name = f"{user_info['data'].get('department')}_{user_info['data'].get('div')}_{user_info['data'].get('year')}_att-{user_info.get('file_name_og')}"
            saved_files = os.listdir("attachments")
            logger.debug(f"Saved files: {saved_files}")
            for file in saved_files:
                cleaned_name = re.sub(r"date-\d{8}-\d{6}_", "", file)
                logger.debug(f"Cleaned name: {cleaned_name}")
                if cleaned_name == file_name:
                    logger.info(f"File {file_name} found")
                    return APIResponse.success(data=os.path.join(f"attachments", file))
                    # return os.path.join("attachments", file)
            logger.info(f"File {file_name} not found")
            return APIResponse.error(f"File {file_name} not found")
        except Exception as e:
            logger.error("Failed to get schedules with error message: {}".format(e))
            return APIResponse.error(f"Failed to get schedules with error message: {e}")

    async def schedule_tt(self,schedule,calendar_id="primary"):

        try:
            today = datetime.today()
            days_until_monday = (0 - today.weekday()) % 7  # Find next Monday
            week_start = today + timedelta(days=days_until_monday)

            for day_schedule in schedule:
                for day, events in day_schedule.items():
                    event_date = get_next_weekday(week_start, day)
                    for event in events:
                        await create_event(
                            service=self.calendar_service,
                            calendar_id=calendar_id,
                            event_date=event_date,
                            start_time=event["start_time"],
                            end_time=event["end_time"],
                            subject=event["name"],
                            # day_code=day
                        )
                    logger.info(f"Created event {day}")
            return APIResponse.success()
        except Exception as e:
            logger.error("Failed to schedule tt event: {}".format(e))

    async def delete_tt(self,user_id:str,calendar_id="primary"):
        try:

            if not self.calendar_service:
                self.get_service(user_id=user_id)
            events_result = self.calendar_service.events().list(
                calendarId=calendar_id,
                q=TAG,  # Free-text search for the tag
                singleEvents=False  # Return recurring event series, not individual instances
            ).execute()

            events = events_result.get('items', [])
            if not events:
                logger.info("No events found with the specified tag.")
                return

            for event in events:
                description = event.get('description', '')
                if description.endswith(f"\n{TAG}"):
                    self.calendar_service.events().delete(
                        calendarId=calendar_id,
                        eventId=event['id']
                    ).execute()

                    logger.info(f"Deleted event summary: {event['summary']}  And ID: {event['id']}")
                else:
                    logger.debug(f"Skipped event summary: {event['summary']}  And ID: {event['id']}: description does not match.")
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            raise