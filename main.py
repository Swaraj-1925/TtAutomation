import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query ,Depends
from fastapi.responses import RedirectResponse
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.db.session import get_session, create_db_and_tables
from app.routes.g_auth import ga_router
from app.routes.g_calender import gc_router
from app.routes.g_gmail import gg_router
from app.services.gmail import get_all_emails
from app.services.google_services import GoogleServices
from app.services.tt_automation import TtAutomation
from app.settings import Settings
from app.utils.handle_file import extract_data_from_xlsx
from app.utils.logger import logger
from app.utils.response import APIResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()  # Initialize DB
    yield
    logger.info("Shutting down lifespan")
app = FastAPI(lifespan=lifespan)
app.include_router(gg_router)  # Include Gmail router
app.include_router(gc_router)  # Include Calendar router
app.include_router(ga_router)
settings = Settings()

@app.get("/")
async def root(
        user_id: str = Query("anonymous", description="User Name"),
        department: str = Query(None, description="Department Name"),
        division: str = Query(None, description="Division Name"),
        year:str = Query(None, description="Student Year"),
        session:AsyncSession = Depends(get_session),
):

    tt_automation = TtAutomation(settings=settings)
    service_response = tt_automation.get_service(user_id=user_id)

    new_user=User(
        username=user_id,
        department=department,
        year=year,
        div=division,
    )
    await tt_automation.save_user_info(new_user,session=session)
    if service_response["code"] == status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED:
        return RedirectResponse(url=service_response.get("data"))

    if service_response["code"] == status.HTTP_200_OK:
        logger.debug(f"Found service")
        return {"service": "hello"}

    return service_response, service_response["statusCode"]

@app.get("/home")
async def home(user_id: str = Query("anonymous", description="User identifier"),session: AsyncSession =Depends(get_session)):
    tt_automation = TtAutomation(settings=settings)
    data = get_all_emails(tt_automation,max_results=10,user_id=user_id)
    user_info = await tt_automation.get_user_info(user_id=user_id,session=session)
    if data:
        msg_id = data[0].get("id")
        attachment_id = data[0].get("attachments", [])[0].get("attachmentId")
        file_name_og = data[0].get("attachments", [])[0].get("filename")
        user_info.update({"file_name_og": file_name_og})

        schedule = tt_automation.get_schedule(file_name_og=file_name_og,user_info=user_info)
        if schedule:
            extracted_data = await extract_data_from_xlsx(file_name=schedule, user_info=user_info)
        else:
            saved_file_path = await tt_automation.get_attachment(user_id=user_id, msg_id=msg_id,
                                                                 attachment_id=attachment_id, user_info=user_info)
            extracted_data = await extract_data_from_xlsx(file_name=saved_file_path, user_info=user_info)

        return APIResponse.success(extracted_data)
    else:
        logger.warning("No data")
        return APIResponse.error("Found no emails",status_code=status.HTTP_204_NO_CONTENT)
