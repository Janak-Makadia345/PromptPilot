import os
import re
import logging
from langchain.prompts import PromptTemplate
from core.prompt_templates.file_analyzer_template import file_analysis_prompt_template
from PyPDF2 import PdfReader

class FileAnalyzerAgent:
    def __init__(self, llm):
        self.logger = logging.getLogger(__name__)
        self.llm = llm
        self.awaiting_file_path = False

        # Load the prompt template once
        self.prompt_template = PromptTemplate.from_template(file_analysis_prompt_template)

    def process(self, prompt: str, context: dict) -> str:
        prompt_lower = prompt.lower()

        # Check if prompt contains 'analyze this file' AND a file path inline
        match = re.search(r'analyze this file[:]?[\s"]*(.+)', prompt_lower)
        if match:
            file_path = match.group(1).strip().strip('"').strip("'")
            if os.path.isfile(file_path):
                return self._read_and_analyze(file_path)
            else:
                self.awaiting_file_path = True
                return f"❌ File not found: {file_path}. Please provide a valid file path."

        # If waiting for file path (after user was prompted)
        if self.awaiting_file_path:
            file_path = prompt.strip().strip('"').strip("'")
            return self._read_and_analyze(file_path)

        # If user just says "analyze this file" without path
        if "analyze this file" in prompt_lower:
            self.awaiting_file_path = True
            return "📂 Please provide the full path to the file you want me to analyze."

        # Default fallback
        return (
            "I can help you analyze files. Please say 'analyze this file' "
            "to start the process."
        )

    def _read_and_analyze(self, file_path: str) -> str:
        if not os.path.isfile(file_path):
            self.awaiting_file_path = False
            return f"❌ File not found: {file_path}. Please try again."

        try:
            content = ""
            if file_path.lower().endswith(".pdf"):
                with open(file_path, "rb") as f:
                    reader = PdfReader(f)
                    for page in reader.pages:
                        content += page.extract_text() + "\n"
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
        except Exception as e:
            self.awaiting_file_path = False
            self.logger.error(f"Error reading file {file_path}: {e}")
            return f"❌ Error reading file: {e}"

        self.awaiting_file_path = False

        # Format prompt and send to LLM
        formatted_prompt = self.prompt_template.format(file_content=content)
        response = self.llm.invoke(formatted_prompt)

        if hasattr(response, "content"):
            return response.content.strip()
        else:
            return str(response).strip()
