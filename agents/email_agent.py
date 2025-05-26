from core.base_agent import BaseAgent
from typing import Dict, Any
from langchain.chains import LLMChain
from langchain.tools import GmailCreateDraft, GmailSendMessage, GmailSearch
import json

class EmailAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt_template,
            memory=self.memory
        )
        self.gmail_draft = GmailCreateDraft()
        self.gmail_send = GmailSendMessage()
        self.gmail_search = GmailSearch()

    def process(self, prompt: str, context: Dict[str, Any] = None) -> str:
        try:
            # Get relevant context
            relevant_emails = self.get_relevant_context(prompt)
            
            if any(word in prompt.lower() for word in ['send', 'write']):
                return self._send_email(prompt, relevant_emails)
            elif any(word in prompt.lower() for word in ['read', 'check', 'search']):
                return self._search_emails(prompt)
            else:
                return "I can help you send or search emails. Please specify what you'd like to do."

        except Exception as e:
            self.logger.error(f"Error processing email request: {str(e)}")
            return f"Failed to process email request: {str(e)}"

    def _send_email(self, prompt: str, context: list) -> str:
        # Use LLM to extract email details
        email_details = self.chain.run(
            input=prompt,
            context=context,
            action="compose_email"
        )
        
        try:
            details = json.loads(email_details)
            
            # Create draft first
            draft = self.gmail_draft.run({
                'to': details['to'],
                'subject': details['subject'],
                'message': details['body']
            })
            
            # Confirm and send
            self.gmail_send.run(draft['id'])
            
            # Save to memory
            self.save_to_memory(prompt, f"Sent email: {details['subject']}")
            
            return f"Email sent successfully to {details['to']}"
            
        except Exception as e:
            raise Exception(f"Failed to send email: {str(e)}")

    def _search_emails(self, prompt: str) -> str:
        try:
            # Use LLM to extract search criteria
            search_query = self.chain.run(
                input=prompt,
                action="extract_search_query"
            )
            
            # Search emails
            results = self.gmail_search.run(search_query)
            
            if not results:
                return "No emails found matching your criteria."
            
            # Format response
            response = "Found emails:\n\n"
            for email in results[:5]:  # Limit to 5 results
                response += f"From: {email['from']}\n"
                response += f"Subject: {email['subject']}\n"
                response += f"Date: {email['date']}\n\n"
            
            return response

        except Exception as e:
            raise Exception(f"Failed to search emails: {str(e)}")