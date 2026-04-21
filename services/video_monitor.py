import cv2
import threading
import time
from ultralytics import YOLO
from services.config import CAMERA_SOURCE, CAMERA_RECONNECT_SECONDS
from services.event_repository import save_event

class VideoMonitor:
    def __init__(self):
        print("🤖 Carregando modelo YOLOv8...")
        # Carrega o modelo nano (mais leve para rodar junto com o Ollama)
        self.model = YOLO("yolov8n.pt") 
        self.current_frame = None
        self.is_running = False
        self.thread = None

    def start(self):
        """Inicia a thread de monitoramento em segundo plano."""
        if self.is_running:
            return
        self.is_running = True
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Para o monitoramento."""
        self.is_running = False
        if self.thread:
            self.thread.join()

    def _update_loop(self):
        """Loop principal de leitura de frames e detecção."""
        while self.is_running:
            print(f"📷 Conectando na fonte: {CAMERA_SOURCE}")
            cap = cv2.VideoCapture(CAMERA_SOURCE)
            
            if not cap.isOpened():
                print(f"⚠️ Falha ao abrir câmera. Reconectando em {CAMERA_RECONNECT_SECONDS}s...")
                time.sleep(CAMERA_RECONNECT_SECONDS)
                continue
            
            print("✅ Conexão estabelecida com o stream!")
            
            while self.is_running and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print("⚠️ Perda de sinal do stream. Tentando reconectar...")
                    break
                
                # Executa a detecção do YOLO no frame atual
                results = self.model(frame, verbose=False)
                
                # Lógica de Persistência: Percorre o que o YOLO encontrou
                for box in results[0].boxes:
                    confianca = float(box.conf[0])
                    
                    # Filtro de confiança (evita salvar falsos positivos)
                    if confianca > 0.20:
                        class_id = int(box.cls[0])
                        label = self.model.names[class_id]
                        
                        # Salva o evento no SQLite (Event Repository)
                        # Por enquanto, image_path fica como placeholder
                        save_event(label, confianca, "static/captures/last_detection.jpg")
                
                # Gera a imagem visual com os quadrados desenhados (anotações)
                annotated_frame = results[0].plot()
                
                # Atualiza o frame atual para o streaming do FastAPI
                self.current_frame = annotated_frame
                
                # Pequena pausa para controle de FPS e alívio da CPU/GPU
                time.sleep(0.03)
                
            cap.release()

# Instância global para ser importada pelo app.py
monitor = VideoMonitor()