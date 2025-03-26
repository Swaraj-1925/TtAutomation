from datetime import timedelta, datetime

from googleapiclient.discovery import Resource

from app.constants import TAG
from app.utils.logger import logger


def get_next_weekday(start_date,day_code):
    day_mapping = {
        "MON": 0,
        "TUE": 1,
        "WED": 2,
        "THURS": 3,
        "FRI": 4,
        "SAT": 5,
        "SUN": 6
    }
    offset = day_mapping.get(day_code.upper(),None)
    if offset is None:
        logger.warning("No offset for {}".format(day_code))
        offset = 0
    event_date = start_date + timedelta(days=offset)
    return event_date.strftime("%Y-%m-%d")

async def create_event(service: Resource,calendar_id, event_date, start_time, end_time, subject, end_date=60):
    start_datetime = datetime.strptime(f"{event_date} {start_time}", "%Y-%m-%d %H:%M")
    end_datetime = datetime.strptime(f"{event_date} {end_time}", "%Y-%m-%d %H:%M")

    end_date = (start_datetime + timedelta(days=60)).strftime("%Y%m%dT000000Z")

    recurrence_rule = [f"RRULE:FREQ=WEEKLY;UNTIL={end_date}"]
    event = {
        "summary": subject,
        "description": f"{subject}\n{TAG}",
        "start": {
            "dateTime": start_datetime.isoformat(),
            "timeZone": "Asia/Kolkata"
        },
        "end": {
            "dateTime": end_datetime.isoformat(),
            "timeZone": "Asia/Kolkata"
        },
        "recurrence": recurrence_rule,
        "colorId": "6"  # Dull Purple Color
    }

    event = service.events().insert(calendarId=calendar_id, body=event).execute()
    logger.info(f"Created event summary: {event['summary']}  And ID: {event['id']}")


