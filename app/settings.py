from  pydantic_settings import  BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    GOOGLE_API_KEY:Optional[str] = None
    GOOGLE_CLIENT_SECRET_FILE:Optional[str] = None
    CALENDAR_NAME:Optional[str] = None
    JAVASCRIPT_ORIGIN:Optional[str] = None
    REDIRECT_URI:Optional[str] = None
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
