import re

class AgentRouter:
    """
    AgentRouter routes the user's prompt to the appropriate agent
    based on comprehensive keyword matching.
    """

    def __init__(self, agents_map=None):
        """
        agents_map: dict[str, agent_instance]
            Maps agent keys to their instances.
        """
        if agents_map is None:
            agents_map = {}
        self.agents_map = agents_map

    def register_agent(self, key, agent):
        """
        Register an agent with a key like 'note_taker', 'email', etc.
        """
        self.agents_map[key] = agent

    def matches_code_intent(self, text: str):
        text_lower = text.lower()
        if "debug" in text_lower and "code" in text_lower:
            return True

        patterns = [
            r"\b(write|generate|create|make)\s+(a\s+)?(python|c\+\+|java|js|javascript|html)?\s*code",
            r"\b(debug|fix)\b.*?\bcode\b",  # updated regex here
            r"\bwhat\s+does\s+(this\s+)?code\s+do",
            r"\bexplain\s+(this\s+)?code",
            r"\b(program|function)\s+(to|in)\b",
            r"\b(code|script)\s+(for|in|to)\b",
        ]
        return any(re.search(p, text.lower()) for p in patterns)


    def route(self, prompt: str):
        """
        Determine the appropriate agent for a prompt.

        Returns:
            agent instance or None if no suitable agent found.
        """
        prompt_lower = prompt.lower()

        # Note Taker
        if any(keyword in prompt_lower for keyword in ["note", "take note", "notes", "reminder"]):
            return self.agents_map.get("note_taker")

        # Email
        email_keywords = [
            "send email", "send mail", "email to", "send an email to",
            "compose email", "compose mail", "email someone", "email",
            "mail", "gmail", "inbox", "check inbox",
            "read emails", "read latest email", "read latest emails",
            "get emails", "emails from", "messages from",
            "check gmail", "get gmail", "fetch email", "fetch gmail",
            "email message", "email conversation", "mail from"
        ]
        if any(keyword in prompt_lower for keyword in email_keywords):
            return self.agents_map.get("email")

        # ✅ Code intent (placed early to avoid calendar false matches)
        if self.matches_code_intent(prompt):
            return self.agents_map.get("code")

        # Web Search
        web_search_keywords = [
            "search for", "look up", "find", "find images of", "show pictures of", 
            "find news about", "what's happening with", "find research papers about", 
            "look for scholarly articles on", "search for", "find best price for", 
            "find", "near me", "what's nearby", "restaurants in", "how to", "guide to",
            "who is", "biography of", "define", "what does", "compare", "difference between",
            "reviews of", "what people say about", "weather in", "events in", "time in",
            "news", "information", "trending", "web", "google"
        ]
        if any(keyword in prompt_lower for keyword in web_search_keywords):
            return self.agents_map.get("web_search")

        # File Analyzer
        if any(keyword in prompt_lower for keyword in ["file", "analyze", "document", "pdf", "text"]):
            return self.agents_map.get("file_analyzer")
        
        # Calendar
        calendar_keywords = {
            "calendar", "schedule", "scheduling", "meeting", "appointment", "event", "reminder",
            "set", "add", "make", "mark", "create", "log", "note down", "add to calendar", 
            "remind me", "remind", "block time", "save the date",
            "my mom's birthday", "dad's birthday", "anniversary", "friend's birthday",
            "bday", "birthday", "exam on", "test on", "interview on", "presentation on",
            "submit on", "due on", "last date", "deadline", "function on", "holiday on",
            "leave on", "trip to", "flight on", "train on", "doctor appointment",
            "dentist appointment", "call with", "zoom with", "teams call", "google meet",
            "on", "at", "from", "to", "between", "next", "tomorrow", "today", "tonight",
            "upcoming", "early morning", "evening", "afternoon", "noon", "midnight",
            "reschedule", "postpone", "change", "move", "update event", "cancel", "delete event",
            "what's on", "what's planned", "what's my schedule", "show calendar", "next event",
            "list my meetings", "my agenda", "show my plan", "event list", "my plans",
            "plan for", "meeting with", "event with", "add note", "reminder for", 
            "set reminder", "schedule with", "add appointment", "fix time",
            "diwali", "eid", "christmas", "new year", "raksha bandhan", "holi", "navratri"
        }
        if any(keyword in prompt_lower for keyword in calendar_keywords):
            return self.agents_map.get("calendar")

        # Fallback
        return self.agents_map.get("default", None)
