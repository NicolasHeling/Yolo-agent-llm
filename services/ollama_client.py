import httpx
import logging
from services.config import OLLAMA_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def chat_with_ollama(messages: list):
    """Envia o contexto e a pergunta para o Ollama local."""
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "num_ctx": 4096  # Limita o uso de RAM
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
            response = await client.post(OLLAMA_URL, json=payload)
            response.raise_for_status() # Lança uma exceção se o status não for 2xx
            
            return response.json()["message"]["content"]
            
    except httpx.HTTPError as e:
        logger.error(f"Erro HTTP na comunicação com Ollama: {e}")
        return "Desculpe, o meu sistema de análise (LLM) está temporariamente indisponível."
    except Exception as e:
        logger.error(f"Erro interno no cliente Ollama: {e}")
        return "Ocorreu uma falha de sistema inesperada ao processar o seu pedido."