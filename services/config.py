import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# --- Configurações da Câmera ---
CAMERA_SOURCE = os.getenv("CAMERA_SOURCE", "0")
CAMERA_RECONNECT_SECONDS = int(os.getenv("CAMERA_RECONNECT_SECONDS", "5"))

# --- Configurações do Ollama (Agente de IA) ---
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))