from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# API Configurations
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
GOOGLE_CALENDAR_CREDENTIALS = os.getenv("GOOGLE_CALENDAR_CREDENTIALS")
GMAIL_CREDENTIALS = os.getenv("GMAIL_CREDENTIALS")

# Model Configurations
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Free HuggingFace model
TEXT_GENERATION_MODEL = "facebook/opt-350m"  # Free HuggingFace model

# FAISS Configuration
FAISS_INDEX_PATH = "data/faiss_index"
DIMENSION = 384  # Dimension for sentence-transformers embeddings

# Application Settings
MAX_HISTORY_LENGTH = 10
MEMORY_K = 5  # Number of relevant memories to retrieve
LOG_FILE = "logs/assistant.log"

# File Paths
NOTES_FILE = "data/notes.json"
UPLOADS_DIR = "data/uploads"

# Prompt Template Paths
PROMPT_TEMPLATE_DIR = "core/prompt_templates"

# Configuration settings
API_KEY = os.getenv('API_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Constants
DEFAULT_LANGUAGE = 'en'
SUPPORTED_LANGUAGES = ['en', 'es', 'fr', 'de']