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
            # Converte a fonte para número (int) se for um dígito como "0"
            source = int(CAMERA_SOURCE) if str(CAMERA_SOURCE).isdigit() else CAMERA_SOURCE
            
            print(f"📷 Conectando na fonte: {source}")
            
            # Ligar diretamente à fonte sem configurações extras do Windows para evitar travamento
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
                
                # Executa a detecção do YOLO
                results = self.model(frame, verbose=False)
                
                # Gera o frame anotado para poder ser guardado
                annotated_frame = results[0].plot()
                
                for box in results[0].boxes:
                    confianca = float(box.conf[0])
                    
                    if confianca > 0.20:
                        class_id = int(box.cls[0])
                        label = self.model.names[class_id]
                        
                        # MELHORIA: Criar um nome de ficheiro único baseado num timestamp
                        timestamp = int(time.time() * 1000)
                        image_filename = f"static/captures/detection_{timestamp}.jpg"
                        
                        # Guarda fisicamente o ficheiro de imagem no disco
                        cv2.imwrite(image_filename, annotated_frame)
                        
                        # Guarda o registo na base de dados referenciando a nova imagem
                        save_event(label, confianca, image_filename)
                
                # Atualiza o frame anotado para a rota de streaming
                self.current_frame = annotated_frame
                time.sleep(0.03)
                
            cap.release()

# Instância global criada no FINAL do arquivo
monitor = VideoMonitor()