interface ChatResponse {
    pergunta: string;
    agente_agrovision: string;
}

const chatWindow = document.getElementById('chat-window') as HTMLDivElement;
const userInput = document.getElementById('user-input') as HTMLInputElement;
const sendBtn = document.getElementById('send-btn') as HTMLButtonElement;

function getTime(): string {
    const now = new Date();
    return now.getHours().toString().padStart(2, '0') + ':' + now.getMinutes().toString().padStart(2, '0');
}

function appendMessage(sender: 'user' | 'bot', text: string, id?: string): void {
    const isBot = sender === 'bot';
    const wrapperClass = isBot ? 'wrapper-bot' : 'wrapper-user';
    const bubbleClass = isBot ? 'bot-msg' : 'user-msg';
    const idAttr = id ? `id="${id}"` : '';

    chatWindow.innerHTML += `
        <div ${idAttr} class="msg-wrapper ${wrapperClass}">
            <span class="msg-time">${getTime()}</span>
            <div class="msg-bubble ${bubbleClass}">${text}</div>
        </div>`;
    
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function sendMessage(): Promise<void> {
    const userText = userInput.value.trim();
    if (!userText) return;

    appendMessage('user', userText);
    userInput.value = '';

    const loadingId = 'loading-' + Date.now();
    const loadingHtml = `
        <div class="typing-indicator">
            <div class="dot"></div><div class="dot"></div><div class="dot"></div>
        </div>`;
    
    appendMessage('bot', loadingHtml, loadingId);

    try {
        const response = await fetch(`/agent/test?q=${encodeURIComponent(userText)}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data: ChatResponse = await response.json();
        
        const loadingElement = document.getElementById(loadingId);
        if (loadingElement) loadingElement.remove();
        
        const formattedResponse = data.agente_agrovision.replace(/\n/g, '<br>');
        appendMessage('bot', formattedResponse);

    } catch (error) {
        const loadingElement = document.getElementById(loadingId);
        if (loadingElement) loadingElement.remove();
        
        chatWindow.innerHTML += `
            <div class="msg-wrapper wrapper-bot">
                <span class="msg-time">${getTime()}</span>
                <div class="msg-bubble bot-msg" style="color: #ef4444;">
                    Falha na comunicação com a API. Verifique os logs do servidor.
                </div>
            </div>`;
        chatWindow.scrollTop = chatWindow.scrollHeight;
        console.error("Erro no chat:", error);
    }
}

// Vincula os eventos aos botões
sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (event: KeyboardEvent) => {
    if (event.key === 'Enter') {
        sendMessage();
    }
});