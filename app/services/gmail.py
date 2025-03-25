from typing import List, Any

from googleapiclient.discovery import Resource

from app.constants import SEARCH_QUERY
from app.services.tt_automation import TtAutomation
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


