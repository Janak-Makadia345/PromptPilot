import re
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
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

        classification_prompt_text = """
You are a note-taking assistant. Given a user's input, classify the command into one of these:
- take: user wants to add a note
- list: user wants to list all notes
- search: user wants to search notes
- delete: user wants to delete a note
- unknown: if none of the above apply

Return only the command keyword: take, list, search, delete, or unknown.

User input: "{input}"

Command:
"""
        self.classification_template = PromptTemplate(
            input_variables=["input"],
            template=classification_prompt_text
        )
        self.classification_chain = LLMChain(llm=llm, prompt=self.classification_template)

    def process(self, prompt: str, context: Optional[Any] = None) -> str:
        print(f"[DEBUG] Received prompt: {prompt}")
        command = self._parse_command(prompt)
        print(f"[DEBUG] Parsed command: {command}")

        if command == "take":
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

        if re.search(r"\b(take|add|create|write|save)\b.*\b(note|memo)\b", prompt_lower):
            return "take"
        if re.search(r"\b(list|show|view|display)\b.*\b(notes?|memos?)\b", prompt_lower):
            return "list"
        if re.search(r"\b(search|find|look up)\b.*\b(notes?|memos?)?\b", prompt_lower):
            return "search"
        if re.search(r"\b(delete|remove|erase)\b.*\b(note|memo)?\b", prompt_lower):
            return "delete"

        try:
            command = self.classification_chain.run({"input": prompt}).strip().lower()
            if command not in {"take", "list", "search", "delete", "unknown"}:
                command = "unknown"
            print(f"[DEBUG] LLM classified command: {command}")
            return command
        except Exception as e:
            print(f"[ERROR] LLM classification failed: {e}")
            return "unknown"

    def _extract_note_content(self, prompt: str) -> str:
        cleaned = re.sub(r"\b(take|add|write|create|save)\b\s*(a)?\s*\b(note|memo)?\b( that| about)?", "", prompt, flags=re.I).strip()
        print(f"[DEBUG] Extracted note content: {cleaned}")
        return cleaned

    def _take_note(self, prompt: str, context: Optional[Any] = None) -> str:
        note_content = self._extract_note_content(prompt)
        context_text = "\n".join(
            doc.page_content if hasattr(doc, "page_content") else str(doc)
            for doc in (context or [])
        )
        current_date = datetime.now().strftime("%Y-%m-%d")

        response = self.chain.run({
            "input": note_content,
            "context": context_text,
            "current_date": current_date
        })

        note_data = self._parse_note_output(response)
        if note_data:
            note_data["date"] = current_date
            self._save_to_local(note_data)
            self._save_to_memory(note_data)
        else:
            print("[ERROR] Unable to parse structured note output.")

        return f"✅ Note taken: {note_data['title']}" if note_data else "Failed to save note."

    def _save_to_memory(self, note_data: Dict[str, str]):
        if not self.vectorstore or not self.embeddings:
            print("[DEBUG] Vectorstore or embeddings not configured, skipping save to memory.")
            return
        from langchain.docstore.document import Document
        content = f"Title: {note_data['title']}\nDate: {note_data['date']}\nTags: {note_data['tags']}\nContent: {note_data['content']}"
        doc = Document(page_content=content)
        self.vectorstore.add_documents([doc])
        print(f"[DEBUG] Saved note titled '{note_data['title']}' to vectorstore.")

    def _save_to_local(self, note_data: Dict[str, str]):
        try:
            with open(self.note_file, 'r+') as f:
                try:
                    notes = json.load(f)
                except json.JSONDecodeError:
                    notes = []
                notes.append(note_data)
                f.seek(0)
                f.truncate()
                json.dump(notes, f, indent=2)
            print(f"[DEBUG] Saved note titled '{note_data['title']}' to local JSON.")
        except Exception as e:
            print(f"[ERROR] Failed to save note locally: {e}")

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
            print(f"[ERROR] Failed to parse note output: {e}")
            return {}

    def _list_notes(self) -> str:
        try:
            with open(self.note_file, 'r') as f:
                notes = json.load(f)
        except Exception:
            notes = []

        if not notes:
            return "No notes found."

        return "\n\n".join(
            f"📝 {note['title']} ({note['date']})\nTags: {note['tags']}\n{note['content']}"
            for note in notes
        )

    import json

    def _search_notes(self, prompt: str) -> str:
        print(f"[DEBUG] Received prompt: {prompt}")
        words = prompt.lower().split()
        stopwords = ["find", "search", "look", "up", "all", "notes", "note", "memos", 
                    "memo", "about", "related", "to", "of", "with", "for", "and", "or", 
                    "the", "a", "an"]

        keywords = [word for word in words if word not in stopwords]
        print(f"[DEBUG] Extracted keywords: {keywords}")

        if not keywords:
            return "Please specify keywords to search for notes."

        try:
            with open(self.note_file, 'r') as f:
                notes = json.load(f)
        except Exception as e:
            print(f"[DEBUG] Error loading notes file: {e}")
            return "No notes found."

        matching_notes = []
        for note in notes:
            combined_text = (note.get('title', '') + " " + note.get('tags', '') + " " + note.get('content', '')).lower()
            print(f"[DEBUG] Checking note: {note.get('title', '')}")
            print(f"[DEBUG] Combined text: {combined_text}")
            # Instead of requiring all keywords, check if ANY keyword is in the note (you can change to ALL if you want)
            if any(k in combined_text for k in keywords):
                matching_notes.append(
                    f"📝 {note.get('title', '')} ({note.get('date', '')})\nTags: {note.get('tags', '')}\n{note.get('content', '')}"
                )

        if matching_notes:
            return "\n\n".join(matching_notes)
        else:
            return f"No relevant notes found for '{' '.join(keywords)}'."


    def _delete_note(self, prompt: str) -> str:
    # Extract potential keyword (e.g., "kabir") from prompt
        keyword = re.sub(r"\b(delete|remove|erase)\b\s*(note|memo)?( of| about| related to| titled)?", "", prompt, flags=re.I).strip()
        if not keyword:
            return "Please specify which note to delete, e.g., 'delete note about Kabir'."

        keyword_lower = keyword.lower()
        try:
            with open(self.note_file, 'r+') as f:
                notes = json.load(f)
                matched_notes = [
                    n for n in notes if (
                        keyword_lower in n['title'].lower()
                        or keyword_lower in n['tags'].lower()
                        or keyword_lower in n['content'].lower()
                    )
                ]
                remaining_notes = [n for n in notes if n not in matched_notes]

                f.seek(0)
                f.truncate()
                json.dump(remaining_notes, f, indent=2)

            if matched_notes:
                deleted_titles = ', '.join(n['title'] for n in matched_notes)
                return f"🗑️ Deleted {len(matched_notes)} note(s) related to '{keyword}': {deleted_titles}"
            else:
                return f"No notes found related to '{keyword}'."
        except Exception as e:
            print(f"[ERROR] Failed to delete note: {e}")
            return "Failed to delete note due to an error."

    
