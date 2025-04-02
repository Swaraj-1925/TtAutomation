import re
from typing import List, Any

import pandas as pd
from googleapiclient.discovery import Resource
from pandas.core.interchange.dataframe_protocol import DataFrame

from app.constants import SEARCH_QUERY
from app.services.tt_automation import TtAutomation
from app.utils.handle_file import extract_data_from_xlsx
from app.utils.logger import logger

def extract_email_data(service: Resource, messages) -> List[Any]:
    email_list = []
    allowed_file_names = ["tt", "time-table", "time tabel", "timetable"]

    for message in messages:
        # Fetch full message details, but only request the fields we need
        msg = service.users().messages().get(
            userId="me",
            id=message["id"],
            fields="id,threadId,labelIds,snippet,payload,internalDate"
        ).execute()

        # Extract headers more efficiently
        headers = msg["payload"]["headers"]
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
        from_addr = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
        # Process attachments more efficiently
        attachments = []
        parts = msg["payload"].get("parts", [])

        for part in parts:
            if part.get("filename") and part.get("body", {}).get("attachmentId"):
                filename = part["filename"].lower()

                if any(allowed_name in filename for allowed_name in allowed_file_names):
                    attachments.append({
                        "filename": part["filename"],
                        "attachmentId": part["body"]["attachmentId"],
                    })

        email_data = {
            "id": msg["id"],
            "threadId": msg["threadId"],
            "labelIds": msg.get("labelIds", []),
            "snippet": msg.get("snippet", ""),
            "subject": subject,
            "from": from_addr,
            "attachments": attachments,
            "internalDate": msg.get("internalDate")
        }

        email_list.append(email_data)
        logger.debug(f"Email Data length: {len(email_data)}")
        if email_list:
            return email_list
        else:
            raise ValueError("No emails found of Time table")

def get_all_emails(automation: TtAutomation,user_id:str,max_results: int = 10):
    try:
        service: Resource = automation.gmail_service
        if not service:
            logger.debug("No Google Mail service")
            automation.get_service(user_id=user_id)
            service = automation.gmail_service

        results = service.users().messages().list(
            userId='me',
            maxResults=max_results,
            q=SEARCH_QUERY
        ).execute()
        messages = results.get("messages")
        msg = extract_email_data(service, messages)
        return msg
    except Exception as e:
        logger.error("Failed to get emails from Google API service with error message: {}".format(e))
        return None


def parse_time(time_str):
    time_str = time_str.strip()
    pattern = re.compile(r'(\d+\.\d{2}) ?(am|pm)', re.IGNORECASE)
    match = pattern.match(time_str)
    if match:
        time_part = match.group(1)
        meridian = match.group(2).lower()
        hour, minute = map(int, time_part.split('.'))
        if meridian == 'am':
            if hour == 12:
                hour = 0
        elif meridian == 'pm':
            if hour != 12:
                hour += 12
        return f"{hour:02d}:{minute:02d}"
    return time_str
def extract_day(day_row,day,target_columns):
    schedule_items = []
    id_counter=1
    for _, row in day_row.iterrows():

        time_range = row['TIME']
        time_range = str(time_range).strip()
        time_range = re.sub(r'\s*-\s*', '-', time_range)
        try:
            start_str, end_str = time_range.split('-')
            start_time = parse_time(start_str)
            end_time = parse_time(end_str)
        except ValueError:
            if time_range != "nan":
                logger.error(f"Invalid time range: {time_range}")
            continue
        subject = row[target_columns]
        if pd.notna(subject) and subject.strip() != '' and subject.strip().lower() != 'lunch break':
            schedule_items.append({
                'id': id_counter,
                'start_time': start_time,
                'end_time': end_time,
                'name': subject.strip()
            })
            id_counter += 1
    return {day: schedule_items}

async def extract_schedule(file_path: str, user_info: dict):
    target_columns = f"{user_info['data'].get('year')} {user_info['data'].get('div')}"
    logger.warning(f"Extracting Schedule from {file_path}")
    tt:DataFrame = await extract_data_from_xlsx(file_path=file_path,target_columns=target_columns)
    unique_days = tt['DAY'].dropna().unique()
    result = []
    for day in unique_days:
        day_rows = tt[tt['DAY'] == day]
        day_tt= extract_day(day_rows, day, target_columns)
        # logger.debug(f"Found {len(day_tt)} rows for day {day_tt}")
        result.append(day_tt)
    return result
