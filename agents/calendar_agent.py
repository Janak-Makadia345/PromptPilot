import os
import pickle
import json
from typing import Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

import dateparser

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from zoneinfo import ZoneInfo  # Python 3.9+ timezone support

from core.prompt_templates.calendar_template import calendar_prompt
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Optional
from datetime import datetime, timedelta

load_dotenv()

class CalendarAgent:
    SCOPES = ['https://www.googleapis.com/auth/calendar']

    def __init__(self, llm: ChatGoogleGenerativeAI, credentials_path=None, token_path="token.pickle"):
        self.llm = llm
        self.credentials_path = credentials_path or os.getenv("GOOGLE_CALENDAR_CREDENTIALS")
        self.token_path = token_path
        self.creds = None
        self.service = None
        self.authenticated = False

    def authenticate_if_needed(self):
        if self.authenticated and self.service:
            return

        if os.path.exists(self.token_path):
            with open(self.token_path, "rb") as token_file:
                self.creds = pickle.load(token_file)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.SCOPES)
                self.creds = flow.run_local_server(port=8080)

            with open(self.token_path, "wb") as token_file:
                pickle.dump(self.creds, token_file)

        self.service = build("calendar", "v3", credentials=self.creds)
        self.authenticated = True

    def extract_event_details(self, text: str) -> Optional[dict]:
        """
        Use LLM to extract event details in JSON format.
        If start or end datetime is missing or relative terms are used,
        parse date/time from text using dateparser with timezone Asia/Kolkata.
        """
        try:
            prompt_filled = calendar_prompt.format(text=text)
            response = self.llm.invoke(prompt_filled)
            content = response.content if hasattr(response, "content") else str(response)

            print("[DEBUG] LLM Output:", content)

            import re
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                content = match.group(0)

            event_data = json.loads(content)

            # Post-process start_datetime and end_datetime for better date/time parsing
            event_data = self._post_process_event_data(event_data, fallback_text=text)

            return event_data

        except Exception as e:
            print(f"[ERROR] Failed to extract event details: {e}")
            return None

    def _post_process_event_data(self, event_data: dict, fallback_text: str) -> dict:
        """
        Ensure start_datetime and end_datetime are ISO strings with timezone info.
        If missing, parse from fallback_text.
        If end_datetime missing, default to 1 hour after start_datetime.
        """

        def parse_datetime(dt_str):
            # Use dateparser to parse date/time string with Asia/Kolkata timezone awareness
            if not dt_str:
                return None
            dt = dateparser.parse(dt_str, settings={"TIMEZONE": "Asia/Kolkata", "RETURN_AS_TIMEZONE_AWARE": True})
            return dt

        start = event_data.get("start_datetime")
        end = event_data.get("end_datetime")

        # Parse start datetime if missing or invalid
        start_dt = parse_datetime(start)
        if not start_dt:
            start_dt = dateparser.parse(fallback_text, settings={"TIMEZONE": "Asia/Kolkata", "RETURN_AS_TIMEZONE_AWARE": True})

        # If still None, fallback to now + 5 minutes
        if not start_dt:
            start_dt = datetime.now(tz=ZoneInfo("Asia/Kolkata")) + timedelta(minutes=5)

        # Parse end datetime or default to 1 hour after start
        end_dt = parse_datetime(end)
        if not end_dt:
            end_dt = start_dt + timedelta(hours=1)

        event_data["start_datetime"] = start_dt.isoformat()
        event_data["end_datetime"] = end_dt.isoformat()

        return event_data

    def create_event(self, event_data: dict) -> dict:
        self.authenticate_if_needed()

        recurrence = event_data.get("recurrence") or ""  # Use empty string if None
        is_yearly_recurring = recurrence.lower() == "yearly"

        if is_yearly_recurring:
            # Convert to all-day event
            # Extract date part only
            start_iso = event_data.get("start_datetime")
            start_date = start_iso.split("T")[0]  # "YYYY-MM-DD"

            start_dt = datetime.fromisoformat(start_date)
            end_dt = start_dt + timedelta(days=1)
            end_date = end_dt.date().isoformat()

            body = {
                "summary": event_data.get("title") or "Untitled Event",
                "location": event_data.get("location"),
                "description": event_data.get("description"),
                "start": {"date": start_date},
                "end": {"date": end_date},
                "recurrence": ["RRULE:FREQ=YEARLY"]
            }
        else:
            # Normal event with dateTime
            body = {
                "summary": event_data.get("title") or "Untitled Event",
                "location": event_data.get("location"),
                "description": event_data.get("description"),
                "start": {
                    "dateTime": event_data.get("start_datetime"),
                    "timeZone": "Asia/Kolkata"
                },
                "end": {
                    "dateTime": event_data.get("end_datetime"),
                    "timeZone": "Asia/Kolkata"
                }
            }

            # Recurrence processing (excluding yearly)
            rrule_map = {
                "daily": "RRULE:FREQ=DAILY",
                "weekly": "RRULE:FREQ=WEEKLY",
                "monthly": "RRULE:FREQ=MONTHLY",
                "yearly": "RRULE:FREQ=YEARLY",
                "every day": "RRULE:FREQ=DAILY",
                "every week": "RRULE:FREQ=WEEKLY",
                "every month": "RRULE:FREQ=MONTHLY",
                "every year": "RRULE:FREQ=YEARLY"
            }

            rrule = None
            if recurrence is None:
                recurrence_lower = ""
            else:
                recurrence_lower = recurrence.lower()
            if recurrence_lower in rrule_map and recurrence_lower != "yearly":
                rrule = rrule_map[recurrence_lower]
            else:
                description = (event_data.get("description") or "").lower()
                for key, rule in rrule_map.items():
                    if key != "yearly" and key in description:
                        rrule = rule
                        break

            if rrule:
                body["recurrence"] = [rrule]

        return self.service.events().insert(calendarId="primary", body=body).execute()

    def list_events(self, max_results=10) -> list:
        self.authenticate_if_needed()
        now = datetime.utcnow().isoformat() + "Z"
        result = self.service.events().list(
            calendarId="primary",
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        return result.get("items", [])

    def update_event(self, event_id: str, event_data: dict) -> dict:
        self.authenticate_if_needed()

        event = self.service.events().get(calendarId='primary', eventId=event_id).execute()

        if "title" in event_data:
            event["summary"] = event_data["title"] or event.get("summary")
        if "description" in event_data:
            event["description"] = event_data["description"]
        if "location" in event_data:
            event["location"] = event_data["location"]

        new_start_iso = event_data.get("start_datetime")
        new_end_iso = event_data.get("end_datetime")

        def has_time(dt_iso):
            return dt_iso and "T" in dt_iso and len(dt_iso.split("T")[1].strip()) > 0

        if new_start_iso:
            is_all_day = "date" in event["start"]

            if is_all_day:
                # all-day event, just update dates
                start_date = new_start_iso.split("T")[0]
                if new_end_iso:
                    end_date = new_end_iso.split("T")[0]
                else:
                    dt = datetime.fromisoformat(start_date)
                    end_date = (dt + timedelta(days=1)).date().isoformat()

                event["start"] = {"date": start_date}
                event["end"] = {"date": end_date}

            else:
                orig_start_str = event["start"].get("dateTime")
                orig_end_str = event["end"].get("dateTime")

                orig_start_dt = datetime.fromisoformat(orig_start_str) if orig_start_str else None
                orig_end_dt = datetime.fromisoformat(orig_end_str) if orig_end_str else None

                new_start_dt = datetime.fromisoformat(new_start_iso)
                new_end_dt = datetime.fromisoformat(new_end_iso) if new_end_iso else None

                if not has_time(new_start_iso) and orig_start_dt:
                    # Update date only, preserve original start time
                    new_start_dt = new_start_dt.replace(
                        hour=orig_start_dt.hour,
                        minute=orig_start_dt.minute,
                        second=orig_start_dt.second,
                        microsecond=orig_start_dt.microsecond,
                    )
                    # For end datetime, preserve original end time but change date to same as new_start_dt date
                    if orig_end_dt:
                        new_end_dt = new_end_dt or orig_end_dt  # fallback to original end if new_end_dt missing
                        new_end_dt = new_end_dt.replace(
                            year=new_start_dt.year,
                            month=new_start_dt.month,
                            day=new_start_dt.day,
                            hour=orig_end_dt.hour,
                            minute=orig_end_dt.minute,
                            second=orig_end_dt.second,
                            microsecond=orig_end_dt.microsecond,
                        )
                    else:
                        # No original end, default 1 hour after new_start_dt on same day
                        new_end_dt = new_start_dt + timedelta(hours=1)

                else:
                    # New start datetime has time — update fully
                    if not new_end_dt:
                        # preserve duration if possible or default 1 hour
                        if orig_start_dt and orig_end_dt:
                            duration = orig_end_dt - orig_start_dt
                            new_end_dt = new_start_dt + duration
                        else:
                            new_end_dt = new_start_dt + timedelta(hours=1)

                event["start"] = {
                    "dateTime": new_start_dt.isoformat(),
                    "timeZone": "Asia/Kolkata"
                }
                event["end"] = {
                    "dateTime": new_end_dt.isoformat(),
                    "timeZone": "Asia/Kolkata"
                }

        recurrence = event_data.get("recurrence")
        rrule_map = {
            "daily": "RRULE:FREQ=DAILY",
            "weekly": "RRULE:FREQ=WEEKLY",
            "monthly": "RRULE:FREQ=MONTHLY",
            "yearly": "RRULE:FREQ=YEARLY"
        }
        recurrence_lower = (recurrence or "").lower()
        if recurrence_lower in rrule_map:
            event["recurrence"] = [rrule_map[recurrence_lower]]
        else:
            event.pop("recurrence", None)

        updated_event = self.service.events().update(
            calendarId='primary',
            eventId=event_id,
            body=event
        ).execute()

        return updated_event

    def search_on_date_and_update(self, title: str, search_date: str, update_date: str, update_time: Optional[str] = None):
        """
        Find event by title on search_date, then update its start/end datetime to update_date (with optional update_time).
        """

        # Build search start_date string (ISO) for exact date match with optional time (none here)
        search_date_iso = f"{search_date}T00:00:00"

        event_id = self.find_event_id(title=title, start_date=search_date_iso)
        if not event_id:
            print(f"Event '{title}' not found on {search_date}")
            return None

        # Prepare new start datetime with or without time
        if update_time:
            new_start = f"{update_date}T{update_time}"
            # For new end datetime, add 1 hour default duration
            new_start_dt = datetime.fromisoformat(new_start)
            new_end_dt = (new_start_dt + timedelta(hours=1)).isoformat()
        else:
            # If no time, just update date, time preserved by update_event
            new_start = f"{update_date}T00:00:00"
            new_end_dt = None

        update_data = {
            "start_datetime": new_start,
            "end_datetime": new_end_dt,
            "title": title
        }

        updated_event = self.update_event(event_id, update_data)
        print(f"Event updated: {updated_event.get('summary')} at {updated_event['start']}")
        return updated_event

    def delete_event(self, event_id: str) -> None:
        self.authenticate_if_needed()
        self.service.events().delete(calendarId="primary", eventId=event_id).execute()

    

    def find_event_id(self, title: str, start_date: Optional[str] = None) -> Optional[str]:
        """
        Search events for one matching the title and optionally datetime (ISO format).
        Return eventId if found, else None.
        """
        self.authenticate_if_needed()

        now = datetime.utcnow().isoformat() + "Z"
        one_year_later = (datetime.utcnow() + timedelta(days=365)).isoformat() + "Z"

        events = self.service.events().list(
            calendarId="primary",
            timeMin=now,
            timeMax=one_year_later,
            maxResults=100,
            singleEvents=False
        ).execute().get("items", [])

        for event in events:
            ev_title = event.get("summary", "").lower()
            ev_start = event["start"].get("dateTime") or event["start"].get("date")
            if not ev_start:
                continue

            ev_start_dt = datetime.fromisoformat(ev_start)

            if title.lower() == ev_title:
                if start_date:
                    try:
                        input_dt = datetime.fromisoformat(start_date)
                    except ValueError:
                        continue

                    # Match date
                    if input_dt.date() != ev_start_dt.date():
                        continue

                    # If time provided, match time too
                    has_time = "T" in start_date and start_date.split("T")[1].strip()
                    if has_time and input_dt.time() != ev_start_dt.time():
                        continue

                return event["id"]

        return None


    def process(self, text: str, context: dict = {}) -> str:
        self.authenticate_if_needed()

        event_data = self.extract_event_details(text)
        if not event_data:
            return "❌ Sorry, I couldn't understand the event details."

        action = event_data.get("action", "create").lower()
        event_id = event_data.get("event_id")

        try:
            if action == "create":
                event = self.create_event(event_data)
                start = event['start'].get('dateTime') or event['start'].get('date')
                return f"✅ Event created: {event.get('summary')} at {start}"

            elif action == "read":
                events = self.list_events()
                if not events:
                    return "📭 No upcoming events found."
                return "\n".join(
                    f"📅 {e.get('summary', 'No Title')} — {e['start'].get('dateTime', e['start'].get('date', ''))}"
                    for e in events
                )

            elif action == "update":
                if not event_id:
                    title = event_data.get("title", "")
                    
                    # Try to get old_date for searching (new key in event_data)
                    old_date = event_data.get("old_start_date")
                    
                    if old_date is None:
                        # fallback: use start_datetime as old_date (may cause failure if date changed)
                        start_dt = event_data.get("start_datetime")
                        old_date = start_dt.split("T")[0] if start_dt else None
                    
                    event_id = self.find_event_id(title=title, start_date=old_date)
                    if not event_id:
                        return "❗ Could not find the event to update. Please provide the event ID or exact title and original date."

                event = self.update_event(event_id, event_data)
                start = event['start'].get('dateTime') or event['start'].get('date')
                return f"✏️ Event updated: {event.get('summary')} at {start}"

            elif action == "delete":
                if not event_id:
                    # Try to find event_id by title and date
                    title = event_data.get("title", "")
                    start_dt = event_data.get("start_datetime")
                    start_date = start_dt.split("T")[0] if start_dt else None

                    event_id = self.find_event_id(title=title, start_date=start_date)
                    if not event_id:
                        return "❗ Could not find the event to delete. Please provide the event ID or exact title and date."

                self.delete_event(event_id)
                return "🗑️ Event deleted."

            else:
                return f"❌ Unknown action '{action}'. Supported actions: create, read, update, delete."

        except Exception as e:
            return f"❌ An error occurred: {str(e)}"
