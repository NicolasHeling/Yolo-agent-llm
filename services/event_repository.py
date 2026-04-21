import sqlite3
from datetime import datetime

# O arquivo do banco de dados será criado na raiz do projeto
DB_PATH = "detections.db"

def init_db():
    """Cria a tabela de eventos se ela não existir."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_time TEXT,
            label TEXT,
            confidence REAL,
            image_path TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("💾 Banco de dados inicializado com sucesso.")

def save_event(label, confidence, image_path=""):
    """Salva uma nova detecção no banco de dados."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Pega a data e hora exata de agora
    event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT INTO events (event_time, label, confidence, image_path)
        VALUES (?, ?, ?, ?)
    ''', (event_time, label, confidence, image_path))
    
    conn.commit()
    conn.close()

def get_recent_events(limit=15):
    """Busca os últimos eventos para mostrar no painel ou para o Agente ler."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, event_time, label, confidence, image_path 
        FROM events 
        ORDER BY id DESC LIMIT ?
    ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    # Transforma o resultado do banco em uma lista de dicionários
    events = []
    for row in rows:
        events.append({
            "id": row[0],
            "event_time": row[1],
            "label": row[2],
            "confidence": round(row[3], 2), # Arredonda para 2 casas decimais
            "image_path": row[4]
        })
    return events