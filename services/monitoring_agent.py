from services.event_repository import get_recent_events
from services.ollama_client import chat_with_ollama
from services.weather_scraper import weather_service

async def build_event_context():
    """Transforma os eventos do banco e o clima em um texto que o Llama entende."""
    
    events = get_recent_events(limit=10)
    context_events = "Últimas detecções do sistema:\n"
    if not events:
        context_events += "Nenhum evento detectado recentemente.\n"
    else:
        for e in events:
            # Arredondamento agora é feito aqui na camada de serviço
            conf = round(e['confidence'], 2)
            context_events += f"- {e['event_time']}: {e['label']} (Confiança: {conf})\n"
            
    clima = await weather_service.get_current_weather()
    if clima["status"] == "success":
        chuva_str = "Sim, chovendo" if clima["is_raining"] else "Tempo limpo/sem chuva"
        context_weather = f"\nCONDIÇÕES METEOROLÓGICAS ATUAIS:\n- Temperatura: {clima['temperature']}°C\n- Vento: {clima['windspeed']} km/h\n- Precipitação: {chuva_str}\n"
    else:
        context_weather = "\nCONDIÇÕES METEOROLÓGICAS: Indisponíveis no momento.\n"
        
    return context_events + context_weather

async def ask_agent(question: str):
    """Prepara o prompt do Agente AgroVision."""
    contexto_completo = await build_event_context()
    
    messages = [
        {
            "role": "system", 
            "content": (
                "Você é o Agente AgroVision, um analista operacional de tráfego. "
                "Seu papel é analisar as detecções, cruzar com as informações meteorológicas e sugerir ações. "
                "Seja direto e use termos técnicos de monitoramento. "
                "Responda sempre em Português do Brasil."
            )
        },
        {"role": "system", "content": f"CONTEXTO ATUAL:\n{contexto_completo}"},
        {"role": "user", "content": question}
    ]
    
    return await chat_with_ollama(messages)