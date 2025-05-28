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

        # Calendar keywords
        if any(keyword in prompt_lower for keyword in ["calendar", "schedule", "meeting", "appointment", "event"]):
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
