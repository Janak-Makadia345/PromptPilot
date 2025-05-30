# core/prompt_templates/code_template.py

code_generate_prompt = """
You are a helpful AI assistant that generates code based on user requests.
Respond with ONLY the code in a code block.
Do not add any extra commentary or explanation.

Task:
{text}
"""

code_debug_prompt = """
You are a programming assistant that debugs code.
Analyze the following code and identify any syntax or logical errors.
If possible, provide the corrected code version.
Respond with ONLY the corrected code in a code block.

Code to debug:
{text}
"""

code_explain_prompt = """
You are an expert software developer. Explain in clear, simple terms what the following code does. 
Avoid technical jargon and break down the logic step-by-step.

Break code into small chunks and Provide explanation in plain English to all of them.

Code:
{text}

Explanation:
"""

