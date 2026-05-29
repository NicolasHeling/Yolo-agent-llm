from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
import uvicorn
import cv2
import time
import os

from services.video_monitor import monitor
from services.event_repository import init_db, get_recent_events
from services.monitoring_agent import ask_agent
from services.agro_scraper import scraper as agro_scraper 
from services.weather_scraper import weather_service      

class ChatRequest(BaseModel):
    q: str = Field(..., min_length=2, max_length=500, description="Pergunta do usuário")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Iniciando motor AgroVision...")
    init_db()        
    monitor.start()  
    yield
    monitor.stop()   

app = FastAPI(title="AgroVision AI - Sistema de Monitoramento", lifespan=lifespan)

templates = Jinja2Templates(directory="templates")

if not os.path.exists("static"):
    os.makedirs("static")
if not os.path.exists("static/captures"):
    os.makedirs("static/captures")
    
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": time.time()}

@app.get("/camera/status")
def camera_status():
    return {
        "online": monitor.current_frame is not None,
        "active_threads": monitor.is_running,
        "source": "California Highway Stream"
    }

@app.get("/events")
def list_events():
    return get_recent_events(limit=20)

@app.post("/agent/chat")
async def chat_agent(request: ChatRequest):
    resposta = await ask_agent(request.q)
    return {
        "pergunta": request.q,
        "agente_agrovision": resposta
    }

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

@app.get("/api/context/agro")
async def get_agro_news():
    dados = await agro_scraper.fetch_agro_context()
    return dados

@app.get("/api/context/weather")
async def get_weather(lat: float = -23.55, lon: float = -46.63):
    clima = await weather_service.get_current_weather(lat, lon)
    return clima

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000)