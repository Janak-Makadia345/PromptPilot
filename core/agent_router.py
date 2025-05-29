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

    def route(self, prompt: str):
        """
        Determine the appropriate agent for a prompt.

        Returns:
            agent instance or None if no suitable agent found.
        """
        prompt_lower = prompt.lower()

        # Note Taker keywords
        if any(keyword in prompt_lower for keyword in ["note", "take note", "notes", "reminder"]):
            return self.agents_map.get("note_taker")

        # Email keywords
        if any(keyword in prompt_lower for keyword in ["email", "send mail", "gmail", "inbox"]):
            return self.agents_map.get("email")

        self.calendar_keywords = {
            # Core calendar terms
            "calendar", "schedule", "scheduling", "meeting", "appointment", "event", "reminder",

            # Real-life phrases for creation
            "set", "add", "make", "mark", "create", "log", "note down", "add to calendar", 
            "remind me", "remind", "block time", "save the date",

            # Specific common usage phrases
            "my mom's birthday", "dad's birthday", "anniversary", "friend's birthday",
            "bday", "birthday", "exam on", "test on", "interview on", "presentation on",
            "submit on", "due on", "last date", "deadline", "function on", "holiday on",
            "leave on", "trip to", "flight on", "train on", "doctor appointment",
            "dentist appointment", "call with", "zoom with", "teams call", "google meet",

            # Time and scheduling cues
            "on", "at", "from", "to", "between", "next", "tomorrow", "today", "tonight",
            "upcoming", "early morning", "evening", "afternoon", "noon", "midnight",

            # Update & Delete
            "reschedule", "postpone", "change", "move", "update event", "cancel", "delete event",

            # View & Read
            "what's on", "what's planned", "what's my schedule", "show calendar", "next event",
            "list my meetings", "my agenda", "show my plan", "event list", "my plans",

            # Fuzzy/natural variants
            "plan for", "meeting with", "event with", "add note", "reminder for", 
            "set reminder", "schedule with", "add appointment", "fix time",

            # Holidays/celebrations
            "diwali", "eid", "christmas", "new year", "raksha bandhan", "holi", "navratri"
        }
        if any(keyword in prompt_lower for keyword in self.calendar_keywords):
            return self.agents_map.get("calendar")


        # Web Search keywords (expanded from your template)
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

        # Code keywords
        if any(keyword in prompt_lower for keyword in ["code", "program", "script", "debug", "compile"]):
            return self.agents_map.get("code")

        # File analyzer keywords
        if any(keyword in prompt_lower for keyword in ["file", "analyze", "document", "pdf", "text"]):
            return self.agents_map.get("file_analyzer")

        # Fallback to a default agent if registered
        return self.agents_map.get("default", None)
