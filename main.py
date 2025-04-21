import os
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, Query ,Depends
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

from sqlmodel import select

from app.db.models import User
from app.db.session import get_session, create_db_and_tables, SessionLocal
from app.routes.g_auth import ga_router
from app.routes.g_calender import gc_router
from app.routes.g_gmail import gg_router
from app.services.gmail import get_all_emails, extract_schedule
from app.services.tt_automation import TtAutomation
from app.settings import Settings
from app.utils.logger import logger
from app.utils.response import APIResponse
from fastapi.middleware.cors import CORSMiddleware
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()  # Initialize DB
    session = SessionLocal()
    logger.info("Initializing background service")
    # background_task = asyncio.create_task(start_background_service(session))
    try:
        yield
    finally:
        # Shutdown: Cancel the background task and close the session
        # background_task.cancel()
        # try:
        #     await background_task
        # except asyncio.CancelledError:
        #     logger.info("Background service cancelled")
        await session.close()
        logger.info("Shutting down lifespan")
    logger.info("Shutting down lifespan")
app = FastAPI(lifespan=lifespan)
app.include_router(gg_router)  # Include Gmail router
app.include_router(gc_router)  # Include Calendar router
app.include_router(ga_router)
settings = Settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this for security
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
async def root(
        user_id: str = Query("anonymous", description="User Name"),
        department: str = Query(None, description="Department Name"),
        division: str = Query(None, description="Division Name"),
        year:str = Query(None, description="Student Year"),
        session:AsyncSession = Depends(get_session),
):
    logger.info("Init")
    tt_automation = TtAutomation(settings=settings)
    service_response = tt_automation.get_service(user_id=user_id)

    new_user=User(
        username=user_id,
        department=department,
        year=year,
        div=division,
        active=True
    )

    await tt_automation.save_user_info(new_user, session=session)
    if service_response["code"] == status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED:
        return APIResponse.auth_required(redirect_url=service_response.get("data"))

    if service_response["code"] == status.HTTP_200_OK:
        logger.debug(f"Found service")
        return APIResponse.success()

    return service_response, service_response["statusCode"]

@app.get("/home")
async def home(user_id: str = Query("anonymous", description="User identifier"),session: AsyncSession =Depends(get_session)):
    tt_automation = TtAutomation(settings=settings)
    data = get_all_emails(tt_automation,max_results=10,user_id=user_id)
    user_info = await tt_automation.get_user_info(user_id=user_id,session=session)
    if data and user_info:
        msg_id = data[0].get("id")
        attachment_id = data[0].get("attachments", [])[0].get("attachmentId")
        file_name_og = data[0].get("attachments", [])[0].get("filename")
        user_info.update({"file_name_og": file_name_og})

        schedule = tt_automation.get_schedule(user_info=user_info)
        logger.debug(schedule)

        if schedule.get('code')==status.HTTP_200_OK:
            extracted_data = await extract_schedule(file_path=schedule.get('data'), user_info=user_info)
        else:
            saved_file_path = await tt_automation.get_attachment(user_id=user_id, msg_id=msg_id,
                                                                 attachment_id=attachment_id, user_info=user_info)
            extracted_data = await extract_schedule(file_path=saved_file_path.get('data'), user_info=user_info)

        await tt_automation.delete_tt(user_id=user_id)
        await tt_automation.schedule_tt(extracted_data,session=session,username=user_info)
        return APIResponse.success(user_info)
    else:
        logger.warning("No data")
        return APIResponse.error("Found no emails",status_code=status.HTTP_204_NO_CONTENT)

@app.get("/delete")
async def delete(user_id: str = Query("anonymous", description="User identifier"),session: AsyncSession =Depends(get_session)):
    tt_automation = TtAutomation(settings=settings)
    user_info = await tt_automation.get_user_info(user_id=user_id,session=session)
    if user_info:
        await tt_automation.delete_tt(user_id=user_id)
        return APIResponse.success("All data deleted",status_code=status.HTTP_204_NO_CONTENT)
    else:
        logger.warning("No user found with id: {}".format(user_id))
        return APIResponse.error("We were unable to find you on our server",status_code=status.HTTP_204_NO_CONTENT)
@app.get("/background_service")
async def start_background_service(session: AsyncSession =Depends(get_session)):
    tt_automation = TtAutomation(settings=settings)
    statement = select(User).where(User.active == True)
    result = await session.execute(statement)
    active_users = result.scalars().all()
    logger.debug(f"Active User count: {len(active_users)} , available users: {active_users}")
    if not active_users:
        await asyncio.sleep(60)
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



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)