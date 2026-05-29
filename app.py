from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import cv2
import time
import os

# Importações dos nossos serviços
from services.video_monitor import monitor
from services.event_repository import init_db, get_recent_events
from services.monitoring_agent import ask_agent
from services.agro_scraper import scraper as agro_scraper # NOVO: Integração do scraper agrícola
from services.weather_scraper import weather_service      # NOVO: Integração do scraper de clima

# 1. Novo sistema de inicialização (Lifespan) que substitui o "on_event"
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Iniciando motor AgroVision...")
    init_db()        # Garante que o SQLite existe
    monitor.start()  # Liga o YOLO e a câmera
    yield
    monitor.stop()   # Desliga a câmera corretamente ao fechar o servidor

app = FastAPI(title="AgroVision AI - Sistema de Monitoramento", lifespan=lifespan)

# Configuração de templates e arquivos estáticos
templates = Jinja2Templates(directory="templates")

if not os.path.exists("static"):
    os.makedirs("static")
if not os.path.exists("static/captures"):
    os.makedirs("static/captures")
    
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Rota Raiz
@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

# 3. Rota de Saúde
@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": time.time()}

# 4. Status da Câmera
@app.get("/camera/status")
def camera_status():
    return {
        "online": monitor.current_frame is not None,
        "active_threads": monitor.is_running,
        "source": "California Highway Stream"
    }

# 5. Histórico de Eventos
@app.get("/events")
def list_events():
    return get_recent_events(limit=20)

# 6. Rota do Agente de IA (Chat)
@app.get("/agent/test")
async def test_agent(q: str = "Resuma o estado atual da via"):
    resposta = await ask_agent(q)
    return {
        "pergunta": q,
        "agente_agrovision": resposta
    }

# 7. Streaming de Vídeo
def generate_frames():
    while True:
        if monitor.current_frame is not None:
            ret, buffer = cv2.imencode('.jpg', monitor.current_frame)
            if ret:
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.04)

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(
        generate_frames(), 
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

# 8. NOVAS ROTAS: Integração da Camada de Web Scraping
@app.get("/api/context/agro")
async def get_agro_news():
    """Retorna as notícias e o contexto de mercado agrícola atual."""
    dados = await agro_scraper.fetch_agro_context()
    return dados

@app.get("/api/context/weather")
async def get_weather(lat: float = -23.55, lon: float = -46.63):
    """Retorna o clima atual de uma coordenada para análise de risco."""
    clima = await weather_service.get_current_weather(lat, lon)
    return clima

# 9. Execução
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000)