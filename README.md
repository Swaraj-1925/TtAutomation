# Time Table Automation for VIIT, Pune

## Introduction

At VIIT, Pune, the timetable is sent via email as an Excel sheet. This project aims to automate the process of extracting the timetable and integrating it with a calendar.



## **Setup Guide**

### **1. Process Overview**
This project automates extracting the VIIT timetable from emails and integrating it with Google Calendar.

**Expected Time Table Format:**  
<a href="attachments/TIME-TABLE-  w.e.f 10-2-2025 V1[Uniq version info]__Expected_tt_format.xlsx">Sample Timetable</a>  

**Workflow Steps:**
1. **Fetch Emails:** Identify and download timetable attachments.
2. **Process Excel File:** Extract and format timetable data.
3. **Integrate with Google Calendar:** Create and manage events.

### **2. Google Cloud Setup**
#### **Step 1: Create a Project in Google Cloud Console**
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Click **New Project** and enter the project name (`TtAutomation`).
3. Enable **Google Calendar API** and **Gmail API**.

#### **Step 2: Setup OAuth Credentials**
1. Navigate to **APIs & Services > Credentials**.
2. Click **Create Credentials > OAuth Client ID**.
3. Choose "Web Application" and add Authorized JavaScript origins. for fastapi `http://localhost:8000 ` and react `http://localhost:5173`
4. Add Authorized redirect URIs as `http://localhost:8000/auth/callback`
5. Download the **Client Secret JSON** file.
6. Move the file to the project root (`TtAutomation/`) and set the path in `.env`:
   ```env
   GOOGLE_CLIENT_SECRET_FILE=path/to/client_secret.json
   ```

### **3. Project Setup**

#### **Step 1: Install Dependencies**
Open a terminal in the project root and run:

**For Windows:**
```sh
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**For Linux/macOS:**
```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### **Step 2: Start Backend (FastAPI)**
```sh
fastapi dev main.py 
```

#### **Step 3: Setup Frontend**
1. Open a new terminal.
2. Navigate to the `user/` directory:
   ```sh
   cd user
   ```
3. Install dependencies:
   ```sh
   npm i
   ```
4. Start the frontend:
   ```sh
   npm run dev
   ```

### **4. Automation Logic**

#### **1. Email Filtering**
- Subject Format: `{Department_Name} Dept - Time Table {Version_Info}`
- Sender: `admin-{Department_Name}@viit.ac.in`

#### **2. Attachment Handling**
- Identify the **Excel (.xlsx) file**.
- Match filename with the email subject.

#### **3. Data Processing**
- Extract timetable structure:
  - **Columns:** Class schedules
  - **Rows:** Days & Time slots
- Convert to **datetime format** for calendar events.

#### **4. Google Calendar Integration**
- **Create/Update Events**


### **5. API Endpoints Used**

#### **Gmail API (Email Handling)**
| Endpoint | Description |
|----------|------------|
| `GET /gmail/v1/users/{userId}/messages` | Fetches email messages. |
| `GET /gmail/v1/users/{userId}/messages/{messageId}` | Retrieves email details & attachments. |
| `GET /gmail/v1/users/{userId}/messages/{messageId}/attachments/{id}` | Downloads an attachment. |

#### **Google Calendar API (Timetable Events)**
| Endpoint | Description |
|----------|------------|
| `POST /calendar/v3/calendars/{calendarId}/events` | Adds timetable events. |
| `PUT /calendar/v3/calendars/{calendarId}/events/{eventId}` | Updates an event. |
| `DELETE /calendar/v3/calendars/{calendarId}/events/{eventId}` | Deletes an event. |

### **6. Expected Output Screenshots**

#### **1. Singup**
<img src="https://github.com/user-attachments/assets/97dfb2d8-1170-4b1e-9252-2bb07e3d987d" width="450"/>

#### **2. Automation done**
<img src="https://github.com/user-attachments/assets/084bf3fe-e489-4b89-9b1d-65a051f54828" width="450"/>

#### **3. Automation deleted**
<img src="https://github.com/user-attachments/assets/8f7e8c53-e0e4-44ec-90c6-403e4ac952d2" width="450"/>

---

### **7. Additional Notes**
- If you encounter errors, ensure all `.env` variables are correctly set.
- Future enhancements include **auto-detection of timetable updates** ,**Set Reminders** (e.g., 10 minutes before class)

