from core.base_agent import BaseAgent
from typing import Dict, Any
from datetime import datetime
import json
import os
from langchain.chains import LLMChain

class NoteTakerAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt_template,
            memory=self.memory
        )
        self.notes_file = "data/notes.json"
        self._ensure_notes_file_exists()

    def process(self, prompt: str, context: Dict[str, Any] = None) -> str:
        try:
            # Get relevant context
            relevant_notes = self.get_relevant_context(prompt)
            
            # Generate response using LLMChain
            response = self.chain.run(
                input=prompt,
                context=relevant_notes,
                current_time=datetime.now().isoformat()
            )

            # Extract note content from response
            note = {
                'timestamp': datetime.now().isoformat(),
                'content': response,
                'tags': self._extract_tags(prompt + " " + response),
                'embedding': self.embeddings.embed_query(response)
            }

            # Save note
            self._save_note(note)
            self.save_to_memory(prompt, response)

            return response

        except Exception as e:
            self.logger.error(f"Error processing note: {str(e)}")
            return f"Failed to process note: {str(e)}"

    def _ensure_notes_file_exists(self):
        os.makedirs(os.path.dirname(self.notes_file), exist_ok=True)
        if not os.path.exists(self.notes_file):
            with open(self.notes_file, 'w') as f:
                json.dump([], f)

    def _save_note(self, note):
        try:
            with open(self.notes_file, 'r+') as f:
                notes = json.load(f)
                notes.append(note)
                f.seek(0)
                json.dump(notes, f, indent=2)

            # Add to vector store
            self.vectorstore.add_texts(
                texts=[note['content']],
                metadatas=[{'timestamp': note['timestamp'], 'tags': note['tags']}]
            )

        except Exception as e:
            raise Exception(f"Failed to save note: {str(e)}")

    def _extract_tags(self, content: str) -> list:
        # Use LLM to extract relevant tags
        tag_prompt = self.prompt_template.format(
            action="extract_tags",
            content=content
        )
        tags_response = self.llm(tag_prompt)
        return [tag.strip() for tag in tags_response.split(',')]