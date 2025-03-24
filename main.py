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
from app.utils.logger import logger
from app.utils.response import APIResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()  # Initialize DB
    yield  # The app runs here
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
    current_time = datetime.datetime.now()
    if data:
        msg_id = data[0].get("id")
        attachment_id = data[0].get("attachments", [])[0].get("attachmentId")
        file_name_og = data[0].get("attachments", [])[0].get("filename")
        file_name = f"{user_info.get('department')}_{user_info.get('div')}_{user_info.get('year')}_date-{current_time.strftime('%Y%m%d-%H%M%S')}_att-{file_name_og}"
        tt_automation.get_attachment(user_id=user_id,msg_id=msg_id,attachment_id=attachment_id,file_name=file_name)
        return APIResponse.success(data=file_name)
    else:
        logger.warning("No data")
        return APIResponse.error("Found no emails",status_code=status.HTTP_204_NO_CONTENT)
