from typing import Dict, Type
from core.base_agent import BaseAgent
import logging
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import LLMChain
from langchain.memory import VectorStoreRetrieverMemory
from langchain.llms import HuggingFaceHub
from langchain.prompts import PromptTemplate
import os
import json

class AgentRouter:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize HuggingFace components
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Initialize FAISS vectorstore
        self.vectorstore = FAISS.from_texts(
            ["Initial context"], 
            embedding=self.embeddings
        )
        
        # Initialize memory
        self.memory = VectorStoreRetrieverMemory(
            retriever=self.vectorstore.as_retriever()
        )
        
        # Initialize LLM
        self.llm = HuggingFaceHub(
            repo_id="google/flan-t5-base",
            huggingfacehub_api_token=os.getenv("HUGGINGFACE_API_KEY")
        )
        
        # Load prompt templates
        self.router_prompt = self._load_prompt_template("router.txt")
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.router_prompt,
            memory=self.memory
        )
        
        # Define agent mappings
        self.agents = {
            'note_taker': {
                'class': 'agents.note_taker_agent.NoteTakerAgent',
                'prompt': 'note_taker.txt'
            },
            'calendar': {
                'class': 'agents.calendar_agent.CalendarAgent',
                'prompt': 'calendar.txt'
            },
            'email': {
                'class': 'agents.email_agent.EmailAgent',
                'prompt': 'email.txt'
            },
            'web_search': {
                'class': 'agents.web_search_agent.WebSearchAgent',
                'prompt': 'web_search.txt'
            },
            'code': {
                'class': 'agents.code_agent.CodeAgent',
                'prompt': 'code.txt'
            },
            'file_analyzer': {
                'class': 'agents.file_analyzer_agent.FileAnalyzerAgent',
                'prompt': 'file_analyzer.txt'
            }
        }

    def route(self, prompt: str) -> BaseAgent:
        """Route the prompt to appropriate agent"""
        try:
            # Get relevant context
            relevant_history = self.memory.load_memory_variables({})
            
            # Classify prompt using LLM
            classification = self.chain.run(
                input=prompt,
                context=relevant_history,
                action="classify"
            )
            
            agent_type = json.loads(classification)['agent']
            
            if agent_type in self.agents:
                self.logger.info(f"Routing to {agent_type} agent")
                return self.initialize_agent(
                    self.agents[agent_type]['class'],
                    self.agents[agent_type]['prompt']
                )
            else:
                raise ValueError(f"No suitable agent found for: {prompt}")
                
        except Exception as e:
            self.logger.error(f"Routing failed: {str(e)}")
            raise

    def initialize_agent(self, agent_class: str, prompt_file: str) -> BaseAgent:
        """Initialize agent with required components"""
        try:
            # Import agent class
            module_name, class_name = agent_class.rsplit('.', 1)
            module = __import__(module_name, fromlist=[class_name])
            agent_cls = getattr(module, class_name)
            
            # Load agent's prompt template
            prompt_template = self._load_prompt_template(prompt_file)
            
            # Initialize agent
            return agent_cls(
                llm=self.llm,
                memory=self.memory,
                prompt_template=prompt_template,
                embeddings=self.embeddings,
                vectorstore=self.vectorstore
            )
            
        except Exception as e:
            self.logger.error(f"Agent initialization failed: {str(e)}")
            raise

    def _load_prompt_template(self, template_file: str) -> PromptTemplate:
        """Load prompt template from file"""
        template_path = f"core/prompt_templates/{template_file}"
        with open(template_path, 'r') as f:
            template_content = f.read()
        return PromptTemplate.from_template(template_content)