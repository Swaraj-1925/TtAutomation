import asyncio

from fastapi import status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.models import User
from app.services.gmail import get_all_emails, extract_schedule
from app.services.tt_automation import TtAutomation
from app.settings import Settings
from app.utils.logger import logger


