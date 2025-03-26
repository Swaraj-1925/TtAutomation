# Define API details as class constants
PG_USERNAME="postgres"
PG_PASSWORD="postgres"
PG_HOST="localhost:5432"
PG_DATABASE="TtAutomation"
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

ADMIN_EMAIL = [
    "admin-csai@viit.ac.in",
    "admin-csaiml@viit.ac.in",
    "admin-ads@viit.ac.in",
    "admin-cese@viit.ac.in",
    "admin-civil@viit.ac.in",
    "admin-comp@viit.ac.in",
    "admin-it@viit.ac.in"
]
SEARCH_QUERY = f'from:{{{ " ".join(ADMIN_EMAIL)}}} "Time table" -Examination has:attachment'

DB_URL = f"postgresql+asyncpg://{PG_USERNAME}:{PG_PASSWORD}@{PG_HOST}/{PG_DATABASE}"

CREATOR_EMAIL = "swaraj.22210249@viit.ac.in'"
TAG = "#TtAutomation"
# TAG = "#CollegeSchedule"
