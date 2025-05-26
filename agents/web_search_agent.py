from core.base_agent import BaseAgent
from typing import Dict, Any
from langchain.chains import LLMChain
from langchain.tools import DuckDuckGoSearchRun
from langchain.utilities import DuckDuckGoSearchAPIWrapper

class WebSearchAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt_template,
            memory=self.memory
        )
        self.search_tool = DuckDuckGoSearchRun(
            api_wrapper=DuckDuckGoSearchAPIWrapper()
        )

    def process(self, prompt: str, context: Dict[str, Any] = None) -> str:
        try:
            # Get relevant context from previous searches
            relevant_searches = self.get_relevant_context(prompt)
            
            # Extract search query using LLM
            search_query = self.chain.run(
                input=prompt,
                context=relevant_searches,
                action="extract_search_query"
            )
            
            # Perform search
            search_results = self.search_tool.run(search_query)
            
            # Summarize results using LLM
            summary = self.chain.run(
                input=search_results,
                context=relevant_searches,
                action="summarize_results"
            )
            
            # Save to memory
            self.save_to_memory(prompt, summary)
            
            return self._format_response(summary, search_results)
            
        except Exception as e:
            self.logger.error(f"Error in web search: {str(e)}")
            return f"Failed to perform web search: {str(e)}"

    def _format_response(self, summary: str, raw_results: str) -> str:
        response = "Search Results:\n\n"
        response += f"Summary: {summary}\n\n"
        response += "Detailed Results:\n"
        
        # Split raw results into digestible chunks
        results = raw_results.split('\n')
        for i, result in enumerate(results[:5], 1):
            response += f"{i}. {result}\n"
        
        return response