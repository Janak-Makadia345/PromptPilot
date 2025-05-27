# core/agent_router.py

class AgentRouter:
    """
    AgentRouter routes the user's prompt to the appropriate agent
    based on simple keyword matching for 6 agents.
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

        if any(keyword in prompt_lower for keyword in ["note", "take note", "notes", "reminder"]):
            return self.agents_map.get("note_taker")

        if any(keyword in prompt_lower for keyword in ["email", "send mail", "gmail", "inbox"]):
            return self.agents_map.get("email")

        if any(keyword in prompt_lower for keyword in ["calendar", "schedule", "meeting", "appointment", "event"]):
            return self.agents_map.get("calendar")

        if any(keyword in prompt_lower for keyword in ["search", "find", "look up", "web", "google"]):
            return self.agents_map.get("web_search")

        if any(keyword in prompt_lower for keyword in ["code", "program", "script", "debug", "compile"]):
            return self.agents_map.get("code")

        if any(keyword in prompt_lower for keyword in ["file", "analyze", "document", "pdf", "text"]):
            return self.agents_map.get("file_analyzer")

        # Fallback to a default agent if registered
        return self.agents_map.get("default", None)
