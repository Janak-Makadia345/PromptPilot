import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

# Load environment variables
load_dotenv()

# Path to save/load FAISS index files
FAISS_INDEX_DIR = os.path.join("data", "faiss_index")

def setup_vectorstore():
    """
    Initialize or load FAISS vector store and embeddings with Google embeddings.
    Returns:
        embeddings: LangChain embeddings instance
        vectorstore: LangChain FAISS vectorstore instance
    """
    # Make sure GOOGLE_API_KEY is available in env
    assert os.getenv("GOOGLE_API_KEY"), "GOOGLE_API_KEY not found in environment!"

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    if os.path.exists(FAISS_INDEX_DIR) and os.listdir(FAISS_INDEX_DIR):
        vectorstore = FAISS.load_local(FAISS_INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
    else:
        vectorstore = FAISS.from_texts(["initial dummy text"], embeddings)
        os.makedirs(FAISS_INDEX_DIR, exist_ok=True)
        vectorstore.save_local(FAISS_INDEX_DIR)

    return embeddings, vectorstore
