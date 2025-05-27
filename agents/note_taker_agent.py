import re
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

from langchain import LLMChain
from core.base_agent import BaseAgent  
from core.prompt_templates.note_taker_template import note_taker_prompt

class NoteTakerAgent(BaseAgent):
    def __init__(
        self,
        llm,
        memory,
        embeddings,
        vectorstore,
        note_file: str = "data/notes.json",
        prompt_template: Optional[Any] = None,
    ):
        template = prompt_template if prompt_template is not None else note_taker_prompt

        super().__init__(llm, memory, template, embeddings, vectorstore)

        self.note_file = note_file
        os.makedirs(os.path.dirname(note_file), exist_ok=True)
        if not os.path.exists(note_file):
            with open(note_file, 'w') as f:
                json.dump([], f)

        self.chain = LLMChain(llm=llm, prompt=template)
        self.embeddings = embeddings
        self.vectorstore = vectorstore

    def process(self, prompt: str, context: Optional[Any] = None) -> str:
        command = self._parse_command(prompt)

        if command == "take":
            # For testing, pass empty context list if None
            return self._take_note(prompt, context if context is not None else [])
        elif command == "list":
            return self._list_notes()
        elif command == "search":
            return self._search_notes(prompt)
        elif command == "delete":
            return self._delete_note(prompt)
        else:
            return "Sorry, I didn't understand that note command."

    def _parse_command(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        if "take note" in prompt_lower:
            return "take"
        elif "show my notes" in prompt_lower:
            return "list"
        elif "find notes about" in prompt_lower:
            return "search"
        elif "delete note" in prompt_lower:
            return "delete"
        return "unknown"

    def _take_note(self, prompt: str, context: Optional[Any] = None) -> str:
        context_text = "\n".join([doc.page_content for doc in context]) if context else ""
        current_date = datetime.now().strftime("%Y-%m-%d")

        response = self.chain.run({
            "input": prompt,
            "context": context_text,
            "current_date": current_date
        })

        # Save note into local json
        self._save_to_local(response)

        # Parse note data to save to vectorstore memory as well
        note_data = self._parse_note_output(response)
        if note_data:
            self._save_to_memory(note_data)

        return response

    def _save_to_memory(self, note_data: Dict[str, str]):
        # Save the note content into vectorstore with embeddings
        if not self.vectorstore or not self.embeddings:
            return
        # Create document with note content
        from langchain.docstore.document import Document
        content = f"Title: {note_data['title']}\nDate: {note_data['date']}\nTags: {note_data['tags']}\nContent: {note_data['content']}"
        doc = Document(page_content=content)
        # Add to vectorstore
        self.vectorstore.add_documents([doc])

    def _save_to_local(self, structured_note: str):
        note_data = self._parse_note_output(structured_note)
        if note_data:
            with open(self.note_file, 'r+') as f:
                try:
                    notes = json.load(f)
                except json.JSONDecodeError:
                    notes = []
                notes.append(note_data)
                f.seek(0)
                f.truncate()
                json.dump(notes, f, indent=2)

    def _parse_note_output(self, text: str) -> Dict[str, str]:
        try:
            title = re.search(r"Title:\s*(.+)", text)
            date = re.search(r"Date:\s*(.+)", text)
            tags = re.search(r"Tags:\s*(.+)", text)
            content = re.search(r"Content:\s*(.+)", text, re.DOTALL)

            if not all([title, date, tags, content]):
                raise ValueError("Missing one or more note fields")

            return {
                "title": title.group(1).strip(),
                "date": date.group(1).strip(),
                "tags": tags.group(1).strip(),
                "content": content.group(1).strip()
            }
        except Exception as e:
            print(f"Failed to parse note output: {e}")
            return {}

    def _list_notes(self) -> str:
        try:
            with open(self.note_file, 'r') as f:
                notes = json.load(f)
        except Exception:
            notes = []

        if not notes:
            return "No notes found."

        return "\n\n".join([f"📌 {note['title']} - {note['date']}" for note in notes])

    def _search_notes(self, prompt: str) -> str:
        query = prompt.lower().replace("find notes about", "").strip()
        if self.vectorstore:
            results = self.vectorstore.similarity_search(query, k=3)
            if results:
                return "\n\n".join([r.page_content for r in results])
            else:
                return f"No notes found about '{query}'."
        else:
            return "No vectorstore configured for search."

    def _delete_note(self, prompt: str) -> str:
        title_to_delete = prompt.lower().replace("delete note", "").strip()

        def normalize(s):
            return s.lower().strip()

        try:
            with open(self.note_file, 'r+') as f:
                notes = json.load(f)
                new_notes = [n for n in notes if normalize(n['title']) != normalize(title_to_delete)]
                f.seek(0)
                f.truncate()
                json.dump(new_notes, f, indent=2)
        except Exception:
            return "Failed to delete note due to file error."

        if len(new_notes) < len(notes):
            return f"Note titled '{title_to_delete}' deleted."
        else:
            return f"No note titled '{title_to_delete}' found."

