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
from app.services.gmail import get_all_emails, extract_schedule
from app.services.tt_automation import TtAutomation
from app.settings import Settings
from app.utils.logger import logger
from app.utils.response import APIResponse
from fastapi.middleware.cors import CORSMiddleware
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
    )
    await tt_automation.save_user_info(new_user,session=session)
    if service_response["code"] == status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED:
        return APIResponse.auth_required(redirect_url=service_response.get("data"))

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

        schedule = tt_automation.get_schedule(user_info=user_info)
        logger.debug(schedule)

        if schedule.get('code')==status.HTTP_200_OK:
            extracted_data = await extract_schedule(file_path=schedule.get('data'), user_info=user_info)
        else:
            saved_file_path = await tt_automation.get_attachment(user_id=user_id, msg_id=msg_id,
                                                                 attachment_id=attachment_id, user_info=user_info)
            extracted_data = await extract_schedule(file_path=saved_file_path.get('data'), user_info=user_info)

        await tt_automation.delete_tt(user_id=user_id)
        await tt_automation.schedule_tt(extracted_data)
        return APIResponse.success(extracted_data)
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

