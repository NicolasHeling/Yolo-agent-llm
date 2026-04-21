from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import cv2
import time
import os

# Importações dos nossos serviços
from services.video_monitor import monitor
from services.event_repository import init_db, get_recent_events
from services.monitoring_agent import ask_agent

app = FastAPI(title="AgroVision AI - Sistema de Monitoramento")

# Configuração de templates e arquivos estáticos
# Certifique-se de que a pasta 'templates' e 'static' existam na raiz
templates = Jinja2Templates(directory="templates")

if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# 1. Evento de inicialização
@app.on_event("startup")
def startup_event():
    print("🚀 Iniciando motor AgroVision...")
    init_db()  # Garante que o SQLite existe
    monitor.start()  # Liga o YOLO e a câmera

# 2. Rota Raiz - AGORA CARREGA O DASHBOARD
@app.get("/")
def read_root(request: Request):
    # Renderiza o arquivo templates/index.html
    return templates.TemplateResponse("index.html", {"request": request})

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

# 8. Execução
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)