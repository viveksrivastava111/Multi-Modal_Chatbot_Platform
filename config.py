"""
Central configuration for the Multi-Modal Chatbot Platform.
Keeps model names, paths, and defaults in one place so modules stay clean.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- API / connection settings -------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "") or None
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# --- Model choices shown in the sidebar ----------------------------------------
OPENAI_MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
OLLAMA_MODELS = ["llama3.1", "llama3.2", "mistral", "phi3"]

DEFAULT_PROVIDER = "OpenAI" if OPENAI_API_KEY else "Ollama"

# --- Embeddings (FastEmbed – small, fast, runs locally, no API key needed) -----
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

# --- Paths ----------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SAMPLE_DB_PATH = os.path.join(DATA_DIR, "sample.db")
VECTOR_STORE_DIR = os.path.join(DATA_DIR, "vector_store")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

# --- RAG settings -----------------------------------------------------------------
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
RETRIEVER_TOP_K = 4

# --- App metadata ------------------------------------------------------------------
APP_TITLE = "Multi-Modal Chatbot Platform"
APP_ICON = "🧠"
MODULES = [
    "💬 General Chat",
    "📄 Document Q&A (RAG)",
    "🗃️ SQL Query Assistant",
    "🌐 Web Search Assistant",
    "🖼️ Image Analysis",
    "📝 Text Summarizer",
]
