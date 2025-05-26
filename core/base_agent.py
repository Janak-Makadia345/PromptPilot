from abc import ABC, abstractmethod
from typing import Dict, Any
from langchain.llms import HuggingFaceHub
from langchain.memory import VectorStoreRetrieverMemory
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
import logging

class BaseAgent(ABC):
    def __init__(
        self,
        llm: HuggingFaceHub,
        memory: VectorStoreRetrieverMemory,
        prompt_template: PromptTemplate,
        embeddings: HuggingFaceEmbeddings,
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
        """Process the input prompt and return a response"""
        pass

    def save_to_memory(self, prompt: str, response: str) -> None:
        """Save interaction to vector memory"""
        self.memory.save_context(
            {"input": prompt},
            {"output": response}
        )

    def get_relevant_context(self, prompt: str) -> list:
        """Retrieve relevant context from memory"""
        return self.vectorstore.similarity_search(prompt, k=3)