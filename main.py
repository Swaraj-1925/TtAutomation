from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse
from fastapi import status

from app.routes.g_auth import ga_router
from app.routes.g_calender import gc_router
from app.routes.g_gmail import gg_router
from app.services.gmail import get_all_emails
from app.services.google_services import GoogleServices
from app.services.tt_automation import TtAutomation
from app.settings import Settings

app = FastAPI()
app.include_router(gg_router)  # Include Gmail router
app.include_router(gc_router)  # Include Calendar router
app.include_router(ga_router)
settings = Settings()


@app.get("/")
async def root(user_id: str = Query("anonymous", description="User identifier")):
    tt_automation = TtAutomation(settings=settings, user_id=user_id)  # Pass user_id here
    service_response = tt_automation.get_service()  # No need to pass prefix separately

    if service_response["code"] == status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED:
        return RedirectResponse(url=service_response.get("data"))

    if service_response["code"] == status.HTTP_200_OK:
        print("Found service")
        return {"service": "hello"}

    return service_response, service_response["statusCode"]

@app.get("/home")
async def home(user_id: str = Query("anonymous", description="User identifier")):
    tt_automation = TtAutomation(settings=settings, user_id=user_id)  # Pass user_id here
    data = get_all_emails(tt_automation,10)
    return {"service": f"home {data}"}

# if __name__ == '__main__':
#     print_hi('PyCharm')