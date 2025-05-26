from typing import Dict, Any, Optional
from core.agent_router import AgentRouter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
import logging
import json
import time
from datetime import datetime

class Orchestrator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.router = AgentRouter()
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vectorstore = FAISS.from_texts(
            ["Conversation history initialization"], 
            embedding=self.embeddings
        )
        self.conversation_history = []

    def process_prompt(self, prompt: str) -> Dict[str, Any]:
        """Process user prompt and return response"""
        start_time = time.time()
        
        try:
            # Save prompt to history
            self.conversation_history.append({
                'role': 'user',
                'content': prompt,
                'timestamp': datetime.now().isoformat()
            })
            
            # Get relevant context
            relevant_history = self.vectorstore.similarity_search(prompt, k=3)
            
            # Route to appropriate agent
            agent = self.router.route(prompt)
            
            # Process with agent
            response = agent.process(prompt, {
                'history': relevant_history,
                'timestamp': datetime.now().isoformat()
            })
            
            # Save response to history
            self.conversation_history.append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now().isoformat(),
                'agent': agent.__class__.__name__
            })
            
            # Update vector store
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
        """Get recent conversation history"""
        if limit:
            return self.conversation_history[-limit:]
        return self.conversation_history

    def save_history(self, filepath: str) -> None:
        """Save conversation history to file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.conversation_history, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save history: {str(e)}")
            raise

    def load_history(self, filepath: str) -> None:
        """Load conversation history from file"""
        try:
            with open(filepath, 'r') as f:
                self.conversation_history = json.load(f)
                
            # Rebuild vector store with loaded history
            conversations = [
                f"User: {turn['content']}\nAssistant: {next_turn['content']}"
                for turn, next_turn in zip(
                    self.conversation_history[::2],
                    self.conversation_history[1::2]
                )
            ]
            
            self.vectorstore = FAISS.from_texts(
                conversations,
                embedding=self.embeddings
            )
            
        except Exception as e:
            self.logger.error(f"Failed to load history: {str(e)}")
            raise