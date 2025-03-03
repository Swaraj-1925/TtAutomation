# Define API details as class constants
GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",  # Read emails for timetables
    "https://www.googleapis.com/auth/gmail.modify",  # Manage processed timetables
]
CALENDAR_SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",  # Manage calendar events
]

API_DETAILS = {
    "gmail": {"service_name": "gmail", "version": "v1", "scopes": GMAIL_SCOPES},
    "calendar": {"service_name": "calendar", "version": "v3", "scopes": CALENDAR_SCOPES},
}
