import os
from datetime import datetime
from typing import Optional, Dict, Any

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env

from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
from serpapi import GoogleSearch

# Assuming you have a BaseAgent class somewhere
class BaseAgent:
    pass


class WebSearchAgent(BaseAgent):
    def __init__(
        self,
        llm: ChatGoogleGenerativeAI,
        memory: Optional[Any] = None,
        prompt_template: Any = None,
        serpapi_api_key: Optional[str] = None,
    ):
        self.llm = llm
        self.memory = memory
        self.chain = LLMChain(llm=self.llm, prompt=prompt_template)
        self.api_key = serpapi_api_key or os.getenv("SERPAPI_API_KEY")
        if not self.api_key:
            raise ValueError("SERPAPI_API_KEY not set in environment")

    def serpapi_search(self, query: str) -> dict:
        params = {
            "engine": "google",
            "q": query,
            "api_key": self.api_key,
            "num": 10,
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        return results

    def process(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        print("🔍 [WebSearchAgent] Processing prompt:", prompt)
        context_str = context.get("context") if context else "None"

        # Step 1: Prepare LLM inputs
        prompt_inputs = {
            "input": prompt,
            "context": context_str,
            "current_date": datetime.now().strftime("%Y-%m-%d"),
        }
        print("🧠 Prompt Inputs to LLM:", prompt_inputs)

        # Step 2: Generate search strategy / query from LLM
        try:
            llm_response = self.chain.invoke(prompt_inputs)
            search_strategy = llm_response["text"].strip()
            print("✅ LLM Output Generated.")
        except Exception as e:
            print("❌ Error during LLM generation:", e)
            return "Failed to generate search strategy."

        # Step 3: Extract the Query line from LLM output (expects a line like "Query: some search terms")
        query_line = next(
            (line for line in search_strategy.splitlines() if line.lower().startswith("query:")),
            None,
        )
        if not query_line:
            return f"❌ Could not find 'Query:' in LLM output.\n\n{search_strategy}"
        query = query_line.split(":", 1)[1].strip()
        print(f"🌐 Extracted Query for search: {query}")

        # Step 4: Perform SerpAPI search and get JSON results
        try:
            results = self.serpapi_search(query)
            print("✅ Search Results received.")
        except Exception as e:
            print("❌ Error during SerpAPI web search:", e)
            return "Failed to fetch search results."

        organic = results.get("organic_results", [])
        if not organic:
            return f"{search_strategy}\n\n---\nNo relevant search results found."

        # Step 5: Format results with title, snippet, and link
        formatted_results = ""
        for idx, res in enumerate(organic[:10], 1):
            title = res.get("title", "No Title")
            snippet = res.get("snippet", "No description available.")
            link = res.get("link", res.get("url", "No link available."))
            formatted_results += f"{idx}. **{title}**\n{snippet}\n🔗 {link}\n\n"

        # Final response string
        return f"{search_strategy}\n\n---\n🔍 Top Search Results:\n{formatted_results.strip()}"
