from fastapi import APIRouter, status, Request, Depends
from fastapi.responses import RedirectResponse

from app.constants import API_DETAILS
from app.services.tt_automation import TtAutomation
from app.settings import Settings

ga_router = APIRouter(prefix="/auth", tags=["authentication"])


# Dependency to get TtAutomation instance
def get_tt_automation(state: str = None) -> TtAutomation:
    settings = Settings()
    user_id = state if state else "anonymous"  # Use state as user_id
    return TtAutomation(settings=settings, user_id=user_id)


@ga_router.get("/callback", summary="Callback endpoint.", status_code=status.HTTP_200_OK)
async def auth_callback(
        request: Request,
        code: str = None,
        error: str = None,
        state: str = None,
        tt_automation: TtAutomation = Depends(get_tt_automation)
):
    """Process the OAuth callback from Google."""
    if error:
        return {"error": error}

    if not code:
        return {"error": "Authorization code not provided"}

    try:
        user_id = tt_automation.handle_auth_callback(code)
        return RedirectResponse(url=f"/home?user_id={user_id}", status_code=status.HTTP_303_SEE_OTHER)

    except Exception as e:
        print(f"Error in callback: {e}")
        return {"error": str(e)}