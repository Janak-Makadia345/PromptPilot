# agents/code_agent.py

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from core.prompt_templates.code_template import (
    code_generate_prompt,
    code_debug_prompt,
    code_explain_prompt
)

load_dotenv()

class CodeAgent:
    def __init__(self, llm: ChatGoogleGenerativeAI):
        """
        Initializes the CodeAgent with a Gemini LLM instance.
        """
        self.llm = llm

    def _invoke_llm(self, prompt: str) -> str:
        """
        Invokes the LLM with the given prompt and returns a clean string.
        """
        try:
            response = self.llm.invoke(prompt)
            result = getattr(response, "content", str(response)).strip()
            return result
        except Exception as e:
            return f"❌ LLM invocation error: {e}"

    def generate_code(self, request: str) -> str:
        """
        Generates code based on a text request.
        """
        prompt = code_generate_prompt.format(text=request)
        return self._invoke_llm(prompt)

    def debug_code(self, buggy_code: str) -> str:
        """
        Debugs and returns corrected code.
        """
        prompt = code_debug_prompt.format(text=buggy_code)
        return self._invoke_llm(prompt)

    def explain_code(self, code_snippet: str) -> str:
        """
        Explains the functionality of a code snippet.
        """
        prompt = code_explain_prompt.format(text=code_snippet)
        return self._invoke_llm(prompt)

    def process(self, text: str, context: dict = {}) -> str:
        """
        Processes a general code-related task based on intent in the text.
        """
        text_lower = text.lower()
        try:
            if "debug" in text_lower or "fix" in text_lower:
                return self.debug_code(text)
            elif "explain" in text_lower or "what does" in text_lower:
                return self.explain_code(text)
            else:
                return self.generate_code(text)
        except Exception as e:
            return f"❌ Error processing code task: {e}"
