from core.base_agent import BaseAgent
from typing import Dict, Any
from langchain.chains import LLMChain
from langchain.tools import PythonREPLTool
import ast
import black

class CodeAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt_template,
            memory=self.memory
        )
        self.python_repl = PythonREPLTool()
        
    def process(self, prompt: str, context: Dict[str, Any] = None) -> str:
        try:
            # Get relevant code context
            relevant_code = self.get_relevant_context(prompt)
            
            if 'explain' in prompt.lower():
                return self._explain_code(prompt, relevant_code)
            elif 'fix' in prompt.lower() or 'debug' in prompt.lower():
                return self._debug_code(prompt, relevant_code)
            else:
                return self._generate_code(prompt, relevant_code)
                
        except Exception as e:
            self.logger.error(f"Error in code processing: {str(e)}")
            return f"Failed to process code request: {str(e)}"

    def _generate_code(self, prompt: str, context: list) -> str:
        # Generate code using LLM
        generated_code = self.chain.run(
            input=prompt,
            context=context,
            action="generate_code"
        )
        
        try:
            # Format code using black
            formatted_code = black.format_str(
                generated_code, 
                mode=black.FileMode()
            )
            
            # Validate syntax
            ast.parse(formatted_code)
            
            # Save to memory
            self.save_to_memory(prompt, formatted_code)
            
            return f"```python\n{formatted_code}\n```"
            
        except Exception as e:
            raise Exception(f"Generated invalid code: {str(e)}")

    def _explain_code(self, prompt: str, context: list) -> str:
        explanation = self.chain.run(
            input=prompt,
            context=context,
            action="explain_code"
        )
        return explanation

    def _debug_code(self, prompt: str, context: list) -> str:
        try:
            # First try to understand the issue
            analysis = self.chain.run(
                input=prompt,
                context=context,
                action="analyze_bug"
            )
            
            # Generate fix
            fix = self.chain.run(
                input=analysis,
                context=context,
                action="generate_fix"
            )
            
            return f"Analysis:\n{analysis}\n\nProposed Fix:\n```python\n{fix}\n```"
            
        except Exception as e:
            raise Exception(f"Debug failed: {str(e)}")