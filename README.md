Markdown
# AgroVision AI 🚜🤖

O **AgroVision AI** é um sistema avançado de monitoramento de tráfego e análise operacional. Este projeto combina **Visão Computacional (YOLOv8)** para detecção de veículos em tempo real com **Inteligência Artificial Generativa Local (Ollama)**, criando um agente inteligente capaz de interpretar eventos, cruzar dados com condições meteorológicas e do mercado agrícola, e sugerir ações operacionais.

---

## 🚀 Funcionalidades Principais

* **Visão Computacional em Tempo Real:** Utiliza o modelo YOLOv8 para detectar objetos (veículos, pessoas, etc.) em um stream de vídeo de uma câmera pública ou local.
* **Agente Operacional Inteligente (LLM):** Integração com o Ollama (modelo Llama) para analisar os eventos detectados e gerar relatórios em linguagem natural.
* **Camada de Web Scraping:** Coleta de dados em tempo real sobre o clima (Open-Meteo) e notícias do mercado agrícola (Notícias Agrícolas) para enriquecer o contexto da IA.
* **Tolerância a Falhas:** A *thread* de captura de vídeo funciona de forma isolada, garantindo que falhas de disco ou de banco de dados não derrubem o monitoramento.
* **Interface Web (Dashboard):** Painel interativo construído com HTML, CSS e TypeScript, se comunicando com o backend através de rotas seguras (POST).

---

## 🛠️ Tecnologias e Arquitetura

O projeto foi construído com uma arquitetura modular focada na separação de responsabilidades:

* **Backend / API:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
* **Visão Computacional:** [Ultralytics YOLOv8](https://docs.ultralytics.com/) e OpenCV
* **IA Generativa Local:** [Ollama](https://ollama.com/) (rodando o modelo `llama3` ou `llama3.2:3b`)
* **Banco de Dados:** SQLite (persistência de eventos com repositório isolado)
* **Frontend:** HTML5, CSS3 e TypeScript puro (compilado para JS)
* **Web Scraping:** `httpx` e `BeautifulSoup4`

---

## ⚙️ Pré-requisitos

Antes de começar, certifique-se de que você tem as seguintes ferramentas instaladas no seu sistema:

* [Python 3.10 ou superior](https://www.python.org/downloads/)
* [Node.js e npm](https://nodejs.org/) (apenas para compilar o TypeScript)
* [Ollama](https://ollama.com/download) instalado e rodando localmente.

---

## 📦 Instalação e Configuração

**1. Clonar o repositório**
```bash
git clone [https://github.com/SEU-USUARIO/Yolo-agent-llm.git](https://github.com/SEU-USUARIO/Yolo-agent-llm.git)
cd Yolo-agent-llm
2. Configurar o Ambiente Virtual Python

Bash
python -m venv .venv
# Ativar no Windows:
.\.venv\Scripts\activate
# Ativar no Linux/Mac:
source .venv/bin/activate
3. Instalar as dependências

Bash
pip install -r requirements.txt
4. Baixar o Modelo do Ollama
Em um terminal separado, garanta que o modelo LLM local foi baixado:

Bash
ollama pull llama3.2:3b
5. Configurar as Variáveis de Ambiente
Crie um arquivo chamado .env na raiz do projeto com o seguinte conteúdo:

Snippet de código
OLLAMA_URL=[http://127.0.0.1:11434/api/chat](http://127.0.0.1:11434/api/chat)
OLLAMA_MODEL=llama3.2:3b
OLLAMA_TIMEOUT=120
OLLAMA_KEEP_ALIVE=30m
AGENT_EVENT_LIMIT=12

# Stream público da rodovia da Califórnia
CAMERA_SOURCE=[https://wzmedia.dot.ca.gov/D11/C214_SB_5_at_Via_De_San_Ysidro.stream/playlist.m3u8](https://wzmedia.dot.ca.gov/D11/C214_SB_5_at_Via_De_San_Ysidro.stream/playlist.m3u8)
CAMERA_RECONNECT_SECONDS=5
6. Compilar o Frontend (TypeScript)

Bash
npx tsc
🚦 Como Executar o Projeto
Certifique-se de que o serviço do Ollama está ativo (ollama serve).

No terminal com o ambiente virtual ativado, inicie o servidor FastAPI:

Bash
python -m uvicorn app:app --reload --port 8000
Abra o seu navegador e acesse o painel de controle:
👉 http://127.0.0.1:8000

🔒 Segurança e Boas Práticas Implementadas
Nesta versão, foram aplicadas diversas melhorias arquiteturais focadas em segurança e estabilidade:

Prevenção de DoS no LLM: O chat com o agente opera agora via método POST com validação estrita de limite de caracteres utilizando a biblioteca Pydantic.

Scraping Ético: A camada de coleta de dados externos possui um limite rigoroso de requisições utilizando cache (Time-to-Live de 1 hora para notícias e 10 minutos para clima), prevenindo a sobrecarga dos servidores públicos e bloqueios de IP.

Isolamento de Banco de Dados: O sistema está protegido contra injeções SQL (SQL Injection), utilizando queries parametrizadas de forma segura na camada event_repository.py.
