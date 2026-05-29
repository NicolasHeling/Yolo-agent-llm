Markdown
# AgroVision AI 🚜🤖

O **AgroVision AI** é um sistema avançado de monitorização de tráfego e análise operacional. Este projeto combina **Visão Computacional (YOLOv8)** para deteção de veículos em tempo real com **Inteligência Artificial Generativa Local (Ollama)**, criando um agente inteligente capaz de interpretar eventos, cruzar dados com condições meteorológicas e do mercado agrícola, e sugerir ações operacionais.

---

## 🚀 Funcionalidades Principais

* **Visão Computacional em Tempo Real:** Utiliza o modelo YOLOv8 para detetar objetos (veículos, pessoas, etc.) num stream de vídeo de uma câmara pública ou local.
* **Agente Operacional Inteligente (LLM):** Integração com o Ollama (modelo Llama) para analisar os eventos detetados e gerar relatórios em linguagem natural.
* **Camada de Web Scraping:** Recolha de dados em tempo real sobre o clima (Open-Meteo) e notícias do mercado agrícola (Notícias Agrícolas) para enriquecer o contexto da IA.
* **Tolerância a Falhas:** A *thread* de captura de vídeo funciona de forma isolada, garantindo que falhas de disco ou de base de dados não derrubem o monitoramento.
* **Interface Web (Dashboard):** Painel interativo construído com HTML, CSS e TypeScript, comunicando com o backend através de rotas seguras (POST).

---

## 🛠️ Tecnologias e Arquitetura

O projeto foi construído com uma arquitetura modular focada na separação de responsabilidades:

* **Backend / API:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
* **Visão Computacional:** [Ultralytics YOLOv8](https://docs.ultralytics.com/) e OpenCV
* **IA Generativa Local:** [Ollama](https://ollama.com/) (executando o modelo `llama3` ou `llama3.2:3b`)
* **Base de Dados:** SQLite (persistência de eventos com repositório isolado)
* **Frontend:** HTML5, CSS3, e TypeScript puro (compilado para JS)
* **Web Scraping:** `httpx` e `BeautifulSoup4`

---

## ⚙️ Pré-requisitos

Antes de começares, certifica-te de que tens as seguintes ferramentas instaladas no teu sistema:

* [Python 3.10 ou superior](https://www.python.org/downloads/)
* [Node.js e npm](https://nodejs.org/) (apenas para compilar o TypeScript)
* [Ollama](https://ollama.com/download) instalado e a correr localmente.

---

## 📦 Instalação e Configuração

**1. Clonar o repositório**
```bash
git clone [https://github.com/TEU-USUARIO/Yolo-agent-llm.git](https://github.com/TEU-USUARIO/Yolo-agent-llm.git)
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
4. Transferir o Modelo do Ollama
Num terminal separado, garante que o modelo LLM está transferido:

Bash
ollama pull llama3.2:3b
5. Configurar as Variáveis de Ambiente
Cria um ficheiro chamado .env na raiz do projeto com o seguinte conteúdo:

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
Certifica-te de que o serviço do Ollama está ativo (ollama serve).

No terminal com o ambiente virtual ativado, inicia o servidor FastAPI:

Bash
python -m uvicorn app:app --reload --port 8000
Abre o teu navegador e acede ao painel de controlo:
👉 http://127.0.0.1:8000

🔒 Segurança e Boas Práticas Implementadas
Nesta versão, foram aplicadas diversas melhorias arquiteturais:

Prevenção de DoS no LLM: O chat com o agente opera agora via método POST com validação estrita de caracteres utilizando a biblioteca Pydantic.

Scraping Ético: A camada de recolha de dados externos possui um limite rigoroso de requisições utilizando cache (Time-to-Live de 1 hora para notícias e 10 minutos para clima), prevenindo a sobrecarga dos servidores públicos.

Isolamento de Base de Dados: O sistema está imune a injeções SQL, utilizando queries parametrizadas na camada event_repository.py.
