from typing import List
import base64

from googleapiclient.discovery import Resource
from app.services.tt_automation import TtAutomation

def extract_email_data(service:Resource,messages, from_filter: str = "admin") -> dict:
    email_list = []
    for message in messages:
        # Fetch full message details
        msg = service.users().messages().get(
            userId="me",
            id=message["id"],
            format="full"
        ).execute()

        # Extract headers
        headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}

        subject = headers.get("Subject", "No Subject")
        from_addr = headers.get("From", "Unknown Sender")
        to_addr = headers.get("To", "Unknown Recipient")
        attachments = []
        if "parts" in msg["payload"]:
            for part in msg["payload"]["parts"]:
                if "filename" in part and part["filename"] and "attachmentId" in part["body"]:
                    attachments.append({
                        "filename": part["filename"],
                        "mimeType": part["mimeType"],
                        "attachmentId": part["body"]["attachmentId"],
                        "size": part["body"].get("size", 0)
                    })

        # Compile email data
        email_data = {
            "id": msg["id"],
            "threadId": msg["threadId"],
            "labelIds": msg.get("labelIds", []),
            "snippet": msg.get("snippet", ""),
            "subject": subject,
            "from": from_addr,
            # "to": to_addr,
            "attachments": attachments,
            "internalDate": msg.get("internalDate")
        }
        email_list.append(email_data)

    return {"emails": email_list}

def get_all_emails(automation: TtAutomation, max_results: int = 10):
    try:
        service: Resource = automation.gmail_service
        if not service:
            print("No gmail service")
            automation.get_service()
            service = automation.gmail_service
        results = service.users().messages().list(
            userId='me',
            maxResults=max_results,
            q= "TIME TABLE"
        ).execute()
        messages = results.get("messages")
        msg = extract_email_data(service, messages)
        return msg["emails"][1]
    except Exception as e:
        print(f"Failed to get emails from Google API service with error message: \n", e)
        pass
