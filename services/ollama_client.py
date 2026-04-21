import httpx
import json
from services.config import OLLAMA_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT

async def chat_with_ollama(messages: list):
    """Envia o contexto e a pergunta para o Ollama local."""
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "num_ctx": 4096  # <-- O Segredo: Limita o uso de RAM para o Llama 3 não travar
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
            response = await client.post(OLLAMA_URL, json=payload)
            
            if response.status_code != 200:
                return f"❌ Ollama recusou (Status {response.status_code}): {response.text}"
                
            return response.json()["message"]["content"]
    except Exception as e:
        return f"❌ Falha na conexão com o servidor Ollama: {str(e)}"