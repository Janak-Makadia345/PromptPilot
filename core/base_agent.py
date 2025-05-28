# core/base_agent.py

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging

from langchain.llms.base import LLM
from langchain.memory import VectorStoreRetrieverMemory
from langchain.embeddings.base import Embeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate


class BaseAgent(ABC):
    """
    Abstract base class for all intelligent agents.
    Provides common methods for memory, logging, and LLM integration.
    """

    def __init__(
        self,
        llm: LLM,
        memory: VectorStoreRetrieverMemory,
        prompt_template: PromptTemplate,
        embeddings: Embeddings,
        vectorstore: FAISS
    ):
        self.llm = llm
        self.memory = memory
        self.prompt_template = prompt_template
        self.embeddings = embeddings
        self.vectorstore = vectorstore
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def process(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """
        Abstract method to be implemented by all child agents.
        Should return a response string.
        """
        pass

    def save_to_memory(self, prompt: str, response: str) -> None:
        """
        Save prompt and its response into vector memory for future context retrieval.
        """
        try:
            self.memory.save_context(
                {"input": prompt},
                {"output": response}
            )
            self.logger.info("Saved interaction to memory.")
        except Exception as e:
            self.logger.error(f"Memory saving failed: {e}")

    def get_relevant_context(self, prompt: str, k: int = 3) -> List[str]:
        """
        Retrieve the top-k most relevant memory snippets from FAISS based on similarity.
        """
        try:
            return self.vectorstore.similarity_search(prompt, k=k)
        except Exception as e:
            self.logger.warning(f"Failed context retrieval from FAISS: {e}")
            return []
