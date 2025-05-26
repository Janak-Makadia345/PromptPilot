from core.base_agent import BaseAgent
from typing import Dict, Any
from datetime import datetime
import json
from langchain.chains import LLMChain
from langchain.tools import GoogleCalendarCreateTool, GoogleCalendarListTool
from dateparser import parse

class CalendarAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt_template,
            memory=self.memory
        )
        self.calendar_create = GoogleCalendarCreateTool()
        self.calendar_list = GoogleCalendarListTool()

    def process(self, prompt: str, context: Dict[str, Any] = None) -> str:
        try:
            # Get relevant context
            relevant_events = self.get_relevant_context(prompt)
            
            # Parse intent
            if any(word in prompt.lower() for word in ['schedule', 'create', 'add']):
                return self._create_event(prompt, relevant_events)
            elif any(word in prompt.lower() for word in ['list', 'show', 'display']):
                return self._list_events(prompt)
            else:
                return "I'm not sure what you want to do with your calendar. Try asking to schedule an event or list upcoming events."

        except Exception as e:
            self.logger.error(f"Error processing calendar request: {str(e)}")
            return f"Failed to process calendar request: {str(e)}"

    def _create_event(self, prompt: str, context: list) -> str:
        # Use LLM to extract event details
        event_details = self.chain.run(
            input=prompt,
            context=context,
            current_time=datetime.now().isoformat(),
            action="create_event"
        )
        
        # Parse event details
        try:
            details = json.loads(event_details)
            # Convert datetime strings to proper format
            start_time = parse(details.get('start_time', 'now'))
            end_time = parse(details.get('end_time', 'now + 1 hour'))
            
            event = {
                'summary': details.get('title', 'Untitled Event'),
                'description': details.get('description', ''),
                'start': {'dateTime': start_time.isoformat()},
                'end': {'dateTime': end_time.isoformat()},
                'attendees': [{'email': email} for email in details.get('attendees', [])]
            }
            
            # Create event using Google Calendar tool
            result = self.calendar_create.run(event)
            
            # Save to memory
            self.save_to_memory(prompt, f"Created event: {event['summary']}")
            
            return f"Event created successfully: {event['summary']}"
        
        except Exception as e:
            raise Exception(f"Failed to create event: {str(e)}")

    def _list_events(self, prompt: str) -> str:
        try:
            # Use LLM to extract time range
            time_range = self.chain.run(
                input=prompt,
                action="extract_time_range"
            )
            
            # Get events using Google Calendar tool
            events = self.calendar_list.run(time_range)
            
            if not events:
                return "No events found for the specified time range."
            
            # Format response
            response = "Upcoming events:\n\n"
            for event in events:
                response += f"- {event['summary']}\n"
                response += f"  When: {event['start'].get('dateTime', event['start'].get('date'))}\n"
                if event.get('description'):
                    response += f"  Description: {event['description']}\n"
                response += "\n"
            
            return response

        except Exception as e:
            raise Exception(f"Failed to list events: {str(e)}")