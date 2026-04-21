from services.event_repository import get_recent_events
from services.ollama_client import chat_with_ollama

def build_event_context():
    """Transforma os eventos do banco em um texto que o Llama entende."""
    events = get_recent_events(limit=10)
    if not events:
        return "Nenhum evento detectado recentemente."
    
    context = "Últimas detecções do sistema:\n"
    for e in events:
        context += f"- {e['event_time']}: {e['label']} (Confiança: {e['confidence']})\n"
    return context

async def ask_agent(question: str):
    """Prepara o prompt do Agente AgroVision."""
    contexto_eventos = build_event_context()
    
    # Este é o 'System Prompt' que define as regras do professor
    messages = [
        {
            "role": "system", 
            "content": (
                "Você é o Agente AgroVision, um analista operacional de tráfego. "
                "Seu papel é analisar as detecções e sugerir ações. "
                "Seja direto e use termos técnicos de monitoramento. "
                "Responda sempre em Português do Brasil."
            )
        },
        {"role": "system", "content": f"CONTEXTO ATUAL: {contexto_eventos}"},
        {"role": "user", "content": question}
    ]
    
    return await chat_with_ollama(messages)