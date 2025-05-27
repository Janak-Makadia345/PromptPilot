import unittest
import os
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import VectorStoreRetrieverMemory
from memory.faiss_store import setup_vectorstore
from agents.note_taker_agent import NoteTakerAgent
from dotenv import load_dotenv
from core.prompt_templates.note_taker_template import note_taker_prompt

load_dotenv()

def load_prompt_template_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read()

class TestNoteTakerAgentGemini(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize Gemini LLM
        cls.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.5,
            convert_system_message_to_human=True
        )

        # Setup vector store and memory
        cls.embeddings, cls.vectorstore = setup_vectorstore()
        cls.memory = VectorStoreRetrieverMemory(retriever=cls.vectorstore.as_retriever())

        # Load prompt template from file
        template_path = os.path.join(os.path.dirname(__file__), "..", "core", "prompt_templates", "note_taker_template.py")
        cls.prompt_template = load_prompt_template_from_file(template_path)

        # Initialize agent
        cls.agent = NoteTakerAgent(
            llm=cls.llm,
            memory=cls.memory,
            embeddings=cls.embeddings,
            vectorstore=cls.vectorstore,
            prompt_template=note_taker_prompt
        )

        cls.test_title = "Test Meeting Note"
        cls.test_tags = "#meeting #test"
        cls.test_date = datetime.now().strftime("%Y-%m-%d")

    def setUp(self):
        # Add a note fresh before each test that needs it
        self.agent.process("take note about test meeting with client")

    def tearDown(self):
        # Delete the test note after each test to keep environment clean
        self.agent.process(f"delete note {self.test_title}")

    def test_1_take_note(self):
        prompt = "take note about test meeting with client"
        response = self.agent.process(prompt)
        self.assertIn("Test Meeting", response)
        self.assertIn("client", response.lower())

    def test_2_list_notes(self):
        prompt = "show my notes"
        response = self.agent.process(prompt)
        # Check the note title appears in list notes response
        self.assertIn("Test Meeting", response)

    def test_3_search_notes(self):
        prompt = "find notes about client"
        response = self.agent.process(prompt)
        self.assertIn("client", response.lower())

    def test_4_delete_note(self):
        prompt = f"delete note {self.test_title}"
        response = self.agent.process(prompt)
        self.assertIn("deleted", response.lower())

    def test_5_verify_deletion(self):
        # Delete first to ensure no note present
        self.agent.process(f"delete note {self.test_title}")
        prompt = "show my notes"
        response = self.agent.process(prompt)
        self.assertNotIn("Test Meeting Note", response)

if __name__ == "__main__":
    unittest.main()
