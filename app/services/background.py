import asyncio

from fastapi import status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.models import User
from app.services.gmail import get_all_emails, extract_schedule
from app.services.tt_automation import TtAutomation
from app.settings import Settings
from app.utils.logger import logger


async def start_background_service(session:AsyncSession):
    settings = Settings()
    tt_automation = TtAutomation(settings=settings)
    while True:
        statement = select(User).where(User.active == True)
        result = await session.execute(statement)
        active_users = result.scalars().all()
        logger.debug(f"Active User count: {len(active_users)} , available users: {active_users}")
        if not active_users:
            await asyncio.sleep(60)
            continue
        for user in active_users:
            user_id = user.username
            logger.info(f"Processing user: {user_id}")
            data = get_all_emails(tt_automation, max_results=10, user_id=user_id)
            if data:
                msg_id = data[0].get("id")
                attachment_id = data[0].get("attachments", [])[0].get("attachmentId")
                file_name_og = data[0].get("attachments", [])[0].get("filename")
                user_info = user.model_dump()
                user_info.update({"file_name_og": file_name_og})
                schedule = tt_automation.get_schedule(user_info=user_info)
                if schedule.get('code') == status.HTTP_200_OK:
                    extracted_data = await extract_schedule(file_path=schedule.get('data'), user_info=user_info)
                else:
                    saved_file_path = await tt_automation.get_attachment(
                        user_id=user_id, msg_id=msg_id, attachment_id=attachment_id, user_info=user_info
                    )
                    extracted_data = await extract_schedule(file_path=saved_file_path.get('data'), user_info=user_info)

                await tt_automation.delete_tt(user_id=user_id)
                await tt_automation.schedule_tt(extracted_data, session=session, username=user_id)
                logger.info(f"Updated timetable for user: {user_id}")
        await asyncio.sleep(900)

