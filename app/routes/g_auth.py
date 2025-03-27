from fastapi import APIRouter, status, Request, Depends
from fastapi.responses import RedirectResponse

from app.constants import API_DETAILS
from app.services.tt_automation import TtAutomation
from app.settings import Settings
from app.utils.logger import logger
from app.utils.response import APIResponse

ga_router = APIRouter(prefix="/auth", tags=["authentication"])



@ga_router.get("/callback", summary="Callback endpoint.", status_code=status.HTTP_200_OK)
async def auth_callback(
        code: str = None,
        error: str = None,
        state: str = None,
):
    if error:
        return {"error": error}
    if not code:
        return {"error": "Authorization code not provided"}
    try:
        settings = Settings()
        tt_automation = TtAutomation(settings=settings)
        user_id = tt_automation.handle_auth_callback(code,user_id=state)
        # return APIResponse.success({"user_id": user_id})
        return RedirectResponse(url=f"http://localhost:5173/home?user_id={user_id}")
        # return RedirectResponse(url=f"/home?user_id={user_id}", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        logger.error("Error handling auth callback \n{}".format(e))
        return {"error": str(e)}