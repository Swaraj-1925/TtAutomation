# Time Table Automation for VIIT, Pune

## Introduction

At VIIT, Pune, the timetable is sent via email as an Excel sheet. This project aims to automate the process of extracting the timetable and integrating it with a calendar.

### Observations:
1. **Email Filtering:**  
   - The subject line for timetable emails follows the format:  
     **`{Department_Name} Dept - Time Table {Version_Info}`**  
   - To improve accuracy, we can add another filter:  
     - The sender should be **`admin-{Department_Name}@viit.ac.in`** (Admin Group).

2. **Attachment Identification:**  
   - Sometimes, the email contains multiple attachments.  
   - The timetable file:  
     - Has the **same name** as the email subject.  
     - It Is always in **Excel (.xlsx) format**.

3. **Excel File Structure:**  
   - The file contains:  
     - **Columns for each class.**  
     - **One column for days.**  
     - **One column for time slots.**  
   - The data needs to be grouped by **days of the week** (seven groups for 7 days).  
   - Convert the extracted data into **datetime format**.

4. **Automation Process:**  
   - Read the **email and extract the timetable file**.  
   - Process the **Excel data** and format it correctly.  
   - Use **Google Calendar API** to upload events for students/teachers.  
   - Set **automatic reminders** (e.g., 10-minute reminders before each class).  

---

## Permissions Required  
To implement this automation, the following permissions are needed:

- **Read emails** (to extract timetable attachments).  
- **Create events** in Google Calendar.  
- **Delete events** in Google Calendar (if updates are needed).  
- **Access student year and department data** (to assign correct events).  


---

## **APIs Used**  
This project primarily uses **Google APIs** to automate the timetable processing. Below is a list of the APIs used along with their descriptions.  

### **1. Gmail API** (For fetching timetable emails and downloading attachments)  
| Endpoint | Description |  
|----------|------------|  
| `GET /gmail/v1/users/{userId}/messages` | Lists the messages in the user's mailbox. Can be filtered using search queries. |  
| `GET /gmail/v1/users/{userId}/messages/{messageId}` | Retrieves details of a specific email, including subject, sender, and attachments. |  
| `GET /gmail/v1/users/{userId}/messages/{messageId}/attachments/{id}` | Downloads an attachment (Excel file) from the specified email. |  

### **2. Google Calendar API** (For creating and managing timetable events)  
| Endpoint | Description |  
|----------|------------|  
| `GET /calendar/v3/users/me/calendarList` | Retrieves a list of all calendars accessible by the user. Helps determine where to upload events. |  
| `POST /calendar/v3/calendars` | Creates a new calendar (e.g., "VIIT Academic Calendar"). Useful if a dedicated calendar is needed. |  
| `POST /calendar/v3/calendars/{calendarId}/events` | Inserts a new event into the specified calendar (timetable entry). |  
| `PUT /calendar/v3/calendars/{calendarId}/events/{eventId}` | Updates an existing event (for timetable changes). |  
| `DELETE /calendar/v3/calendars/{calendarId}/events/{eventId}` | Deletes an event (for canceled classes or rescheduled lectures). |  

### **3. Google OAuth 2.0 API** (For authentication and authorization)  
| Endpoint | Description |  
|----------|------------|  
| `https://accounts.google.com/o/oauth2/auth` | Handles user authentication and authorization to grant access to Gmail and Calendar. |  
| `https://oauth2.googleapis.com/token` | Exchanges an authorization code for an access token to make API requests. |  

