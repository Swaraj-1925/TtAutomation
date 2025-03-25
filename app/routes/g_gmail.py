from fastapi import APIRouter,status
from pydantic_settings import SettingsConfigDict

#google gmail route
gg_router = APIRouter(prefix="/gmail", tags=["gmail"])

@gg_router.get("/get_all_email",summary="Get all emails",status_code=status.HTTP_200_OK)
async def get_all_email(settings: SettingsConfigDict):
    pass

@gg_router.get("/get_email",summary="Get Email",status_code=status.HTTP_200_OK)
async def get_email(settings: SettingsConfigDict):
    pass

@gg_router.get("/get_attachment",summary="Get Attachment",status_code=status.HTTP_200_OK)
async def get_attachment(settings: SettingsConfigDict):
    pass

