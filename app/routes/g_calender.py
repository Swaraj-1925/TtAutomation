from fastapi import APIRouter,status
from pydantic_settings import SettingsConfigDict

#google calender routes
gc_router = APIRouter(prefix="/calendar", tags=["calendar"])

@gc_router.get("/get_calendars",summary="Get all user calendars",status_code=status.HTTP_200_OK)
def get_calendars(settings: SettingsConfigDict):
    pass

@gc_router.post("/create_calendar",summary="Create new user calendar",status_code=status.HTTP_201_CREATED)
def create_calendar(settings: SettingsConfigDict):
    pass

@gc_router.put("/update_calendar",summary="Update user calendar",status_code=status.HTTP_200_OK)
def update_calendar(settings: SettingsConfigDict):
    pass

@gc_router.delete("/delete_calendar",summary="Delete an event from Calender",status_code=status.HTTP_200_OK)
def delete_event(settings: SettingsConfigDict):
    pass
