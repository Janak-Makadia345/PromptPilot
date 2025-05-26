from .faiss_store import FAISSStore
from .embedder import Embedder
from .memory_agent import MemoryAgent

__all__ = [
    'FAISSStore',
    'Embedder',
    'MemoryAgent'
]


class AgentRouter:
    def __init__(self):
        self.agents = {
            'note_taker': 'agents.note_taker_agent.NoteTakerAgent',
            'calendar': 'agents.calendar_agent.CalendarAgent',
            'email': 'agents.email_agent.EmailAgent',
            'web_search': 'agents.web_search_agent.WebSearchAgent',
            'code': 'agents.code_agent.CodeAgent',
            'file_analyzer': 'agents.file_analyzer_agent.FileAnalyzerAgent'
        }

    def route(self, prompt):
        # Logic to classify the prompt and route to the appropriate agent
        agent_type = self.classify_prompt(prompt)
        if agent_type in self.agents:
            agent_class = self.agents[agent_type]
            return self.initialize_agent(agent_class)
        else:
            raise ValueError("No suitable agent found for the prompt.")

    def classify_prompt(self, prompt):
        # Placeholder for prompt classification logic
        # This should return the type of agent based on the prompt
        return 'note_taker'  # Example return value

    def initialize_agent(self, agent_class):
        # Logic to initialize the agent class
        module_name, class_name = agent_class.rsplit('.', 1)
        module = __import__(module_name, fromlist=[class_name])
        agent = getattr(module, class_name)()
        return agent