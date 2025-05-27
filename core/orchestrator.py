import logging
import json
import time
import os
from datetime import datetime
from typing import Dict, Any, Optional

from core.agent_router import AgentRouter
from memory.faiss_store import setup_vectorstore
from dotenv import load_dotenv

# Import all agents and prompt templates
from agents.note_taker_agent import NoteTakerAgent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import VectorStoreRetrieverMemory
from core.prompt_templates.note_taker_template import note_taker_prompt

# Load environment variables from .env file
load_dotenv()

class Orchestrator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.router = AgentRouter()

        # ✅ Initialize embeddings and vectorstore
        self.embeddings, self.vectorstore = setup_vectorstore()

        # ✅ Build LLM and memory (shared across agents)
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.5,
            convert_system_message_to_human=True
        )
        memory = VectorStoreRetrieverMemory(retriever=self.vectorstore.as_retriever())

        # ✅ Register all available agents here
        self._register_agents(llm, memory)

        self.conversation_history = []

    def _register_agents(self, llm, memory):
        """Register all agents here for auto-routing"""
        note_taker = NoteTakerAgent(
            llm=llm,
            memory=memory,
            embeddings=self.embeddings,
            vectorstore=self.vectorstore,
            prompt_template=note_taker_prompt
        )
        self.router.register_agent("note_taker", note_taker)

        # Example: register future agents here
        # from agents.calendar_agent import CalendarAgent
        # self.router.register_agent("calendar", CalendarAgent(...))

    def process_prompt(self, prompt: str) -> Dict[str, Any]:
        """Process user prompt and return response"""
        start_time = time.time()
        try:
            self.conversation_history.append({
                'role': 'user',
                'content': prompt,
                'timestamp': datetime.now().isoformat()
            })

            relevant_history = self.vectorstore.similarity_search(prompt, k=3)
            agent = self.router.route(prompt)

            response = agent.process(prompt, {
                'history': relevant_history,
                'timestamp': datetime.now().isoformat()
            })

            self.conversation_history.append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now().isoformat(),
                'agent': agent.__class__.__name__
            })

            self.vectorstore.add_texts(
                texts=[f"User: {prompt}\nAssistant: {response}"],
                metadatas=[{
                    'timestamp': datetime.now().isoformat(),
                    'agent': agent.__class__.__name__
                }]
            )

            return {
                'response': response,
                'agent': agent.__class__.__name__,
                'processing_time': time.time() - start_time
            }

        except Exception as e:
            self.logger.error(f"Processing failed: {str(e)}")
            return {
                'error': str(e),
                'processing_time': time.time() - start_time
            }

    def get_conversation_history(self, limit: Optional[int] = None) -> list:
        return self.conversation_history[-limit:] if limit else self.conversation_history

    def save_history(self, filepath: str) -> None:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save history: {str(e)}")
            raise

    def load_history(self, filepath: str) -> None:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.conversation_history = json.load(f)

            conversations = [
                f"User: {turn['content']}\nAssistant: {next_turn['content']}"
                for turn, next_turn in zip(
                    self.conversation_history[::2],
                    self.conversation_history[1::2]
                )
            ]

            self.vectorstore = self.vectorstore.from_texts(
                conversations,
                embedding=self.embeddings
            )

        except Exception as e:
            self.logger.error(f"Failed to load history: {str(e)}")
            raise
