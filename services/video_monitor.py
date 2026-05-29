import cv2
import threading
import time
from ultralytics import YOLO
from services.config import CAMERA_SOURCE, CAMERA_RECONNECT_SECONDS
from services.event_repository import save_event

class VideoMonitor:
    def __init__(self):
        print("🤖 Carregando modelo YOLOv8...")
        self.model = YOLO("yolov8n.pt") 
        self.current_frame = None
        self.is_running = False
        self.thread = None

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join()

    def _update_loop(self):
        while self.is_running:
            source = int(CAMERA_SOURCE) if str(CAMERA_SOURCE).isdigit() else CAMERA_SOURCE
            
            print(f"📷 Conectando na fonte: {source}")
            
            cap = cv2.VideoCapture(source)
            
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
                
                results = self.model(frame, verbose=False)
                
                annotated_frame = results[0].plot()
                
                for box in results[0].boxes:
                    confianca = float(box.conf[0])
                    
                    if confianca > 0.20:
                        class_id = int(box.cls[0])
                        label = self.model.names[class_id]
                        
                        try:
                            timestamp = int(time.time() * 1000)
                            image_filename = f"static/captures/detection_{timestamp}.jpg"
                            
                            cv2.imwrite(image_filename, annotated_frame)
                            save_event(label, confianca, image_filename)
                        except Exception as e:
                            print(f"⚠️ Erro ao salvar frame ou gravar evento: {e}")
                            continue
                
                self.current_frame = annotated_frame
                time.sleep(0.03)
                
            cap.release()

monitor = VideoMonitor()