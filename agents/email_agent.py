import os
import pickle
import base64
import re
import logging
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from core.prompt_templates.email_template import email_prompt_template
from langchain.prompts import PromptTemplate


class EmailAgent:
    SCOPES = [
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/gmail.metadata",
        "https://www.googleapis.com/auth/calendar",
        "openid"
    ]

    def __init__(self, llm):
        self.logger = logging.getLogger(__name__)
        self.llm = llm
        self.user_email = None
        self.service = None

    def _ensure_authenticated(self):
        if self.service is None:
            creds = None
            if os.path.exists("token.pickle"):
                with open("token.pickle", "rb") as token:
                    creds = pickle.load(token)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        "core/client_secret.json", self.SCOPES
                    )
                    creds = flow.run_local_server(port=8888)
                with open("token.pickle", "wb") as token:
                    pickle.dump(creds, token)

            self.service = build("gmail", "v1", credentials=creds)
            user_profile = self.service.users().getProfile(userId="me").execute()
            self.user_email = user_profile.get("emailAddress", "unknown")
            self.logger.info(f"Signed in as: {self.user_email}")

    def generate_email(self, recipient: str, subject: str, body: str) -> str:
        prompt = PromptTemplate.from_template(email_prompt_template)
        input_prompt = prompt.format(recipient=recipient, subject=subject, body=body)
        response = self.llm.invoke(input_prompt)

        # Extract and clean LLM response
        if hasattr(response, "content"):
            return response.content.strip()
        elif isinstance(response, str):
            return response.strip()
        else:
            return str(response).strip()

    def send_email(self, to: str, subject: str, message_html: str) -> str:
        self._ensure_authenticated()

        message = MIMEText(message_html, "html")
        message["to"] = to
        message["subject"] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        sent = self.service.users().messages().send(userId="me", body={"raw": raw_message}).execute()
        return f"Email sent to {to}. ID: {sent['id']}"

    def extract_email_and_subject(self, prompt: str):
        pattern = r"(?:send (?:an )?email|send mail)\s+to\s+([^\s]+)\s+.*regarding\s+(.+)"
        match = re.search(pattern, prompt, re.I)
        if match:
            to = match.group(1).strip()
            subject = match.group(2).strip().title()  # Capitalize subject
            return to, subject
        else:
            return None, None


    def process(self, prompt: str, context: dict) -> str:
        to, subject = self.extract_email_and_subject(prompt)
        if not to:
            return "Could not extract a valid email address from the prompt."

        generated_email = self.generate_email(to, subject, prompt)

        print("\n--- Drafted Email (HTML) ---\n")
        print(generated_email)
        print("\n----------------------------\n")

        while True:
            decision = input("Send this email? (yes/edit/cancel): ").strip().lower()
            if decision == "yes":
                return self.send_email(to, subject, generated_email)
            elif decision == "edit":
                revised = input("Enter the revised email content:\n")
                generated_email = self.generate_email(to, subject, revised)
                print("\nUpdated Draft:\n", generated_email)
            elif decision == "cancel":
                return "Cancelled sending email."
            else:
                print("Please enter 'yes', 'edit', or 'cancel'.")

            return "EmailAgent could not handle this prompt."

    def read_latest_emails(self, max_results=5):
        self._ensure_authenticated()
        results = self.service.users().messages().list(userId='me', maxResults=max_results).execute()
        messages = results.get('messages', [])

        emails = []
        for msg in messages:
            msg_data = self.service.users().messages().get(userId='me', id=msg['id']).execute()
            snippet = msg_data.get('snippet', '')
            emails.append(snippet)
        return emails

    def get_emails_from_sender(self, sender_email: str, max_results=5):
        self._ensure_authenticated()
        query = f"from:{sender_email}"
        results = self.service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
        messages = results.get('messages', [])

        emails = []
        for msg in messages:
            msg_data = self.service.users().messages().get(userId='me', id=msg['id']).execute()
            snippet = msg_data.get('snippet', '')
            emails.append(snippet)
        return emails
