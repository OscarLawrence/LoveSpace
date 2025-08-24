class AxiomChat {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.isStreaming = false;
        this.currentAssistantMessage = null;
        
        this.initElements();
        this.initEventListeners();
        this.connect();
    }
    
    initElements() {
        this.chatForm = document.getElementById('chatForm');
        this.messageInput = document.getElementById('messageInput');
        this.chatHistory = document.getElementById('chatHistory');
        this.sendBtn = document.getElementById('sendBtn');
        this.stopBtn = document.getElementById('stopBtn');
        this.clearBtn = document.getElementById('clearBtn');
        this.status = document.getElementById('status');
    }
    
    initEventListeners() {
        this.chatForm.addEventListener('submit', (e) => this.handleSubmit(e));
        this.stopBtn.addEventListener('click', () => this.stopGeneration());
        this.clearBtn.addEventListener('click', () => this.clearHistory());
        
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.chatForm.dispatchEvent(new Event('submit'));
            }
        });
    }
    
    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            this.isConnected = true;
            this.setStatus('Connected', 'success');
            this.requestHistory();
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };
        
        this.ws.onclose = () => {
            this.isConnected = false;
            this.setStatus('Disconnected - Reconnecting...', 'error');
            setTimeout(() => this.connect(), 2000);
        };
        
        this.ws.onerror = (error) => {
            this.setStatus('Connection error', 'error');
        };
    }
    
    handleMessage(data) {
        switch (data.type) {
            case 'message_received':
                this.addMessage('user', data.content);
                this.startStreaming();
                break;
                
            case 'token':
                this.appendToAssistantMessage(data.content);
                break;
                
            case 'tool_calls_detected':
                this.setStatus('Tool calls detected, collecting...', 'info');
                break;
                
            case 'executing_tools':
                this.setStatus('Executing tools...', 'info');
                break;
                
            case 'tool_results':
                this.setStatus('Tools executed, continuing response...', 'info');
                break;
                
            case 'complete':
                this.finishStreaming();
                this.renderConversation(data.conversation);
                this.setStatus('Ready', 'success');
                break;
                
            case 'stopped':
                this.finishStreaming();
                this.setStatus('Generation stopped', 'warning');
                break;
                
            case 'cleared':
                this.chatHistory.innerHTML = '';
                this.setStatus('History cleared', 'info');
                break;
                
            case 'history':
                this.renderConversation(data.conversation);
                break;
                
            case 'stop_requested':
                this.setStatus('Stopping generation...', 'warning');
                break;
        }
    }
    
    handleSubmit(e) {
        e.preventDefault();
        
        if (!this.isConnected || this.isStreaming) return;
        
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        this.sendMessage(message);
        this.messageInput.value = '';
    }
    
    sendMessage(content) {
        if (!this.isConnected) return;
        
        this.ws.send(JSON.stringify({
            type: 'message',
            content: content
        }));
        
        this.setLoading(true);
    }
    
    stopGeneration() {
        if (!this.isConnected || !this.isStreaming) return;
        
        this.ws.send(JSON.stringify({
            type: 'stop'
        }));
    }
    
    clearHistory() {
        if (!this.isConnected) return;
        
        this.ws.send(JSON.stringify({
            type: 'clear'
        }));
    }
    
    requestHistory() {
        if (!this.isConnected) return;
        
        this.ws.send(JSON.stringify({
            type: 'get_history'
        }));
    }
    
    startStreaming() {
        this.isStreaming = true;
        this.currentAssistantMessage = this.addMessage('assistant', '');
        this.stopBtn.disabled = false;
        this.setStatus('Generating response...', 'info');
    }
    
    appendToAssistantMessage(content) {
        if (this.currentAssistantMessage) {
            const contentDiv = this.currentAssistantMessage.querySelector('.content');
            contentDiv.textContent += content;
            this.chatHistory.scrollTop = this.chatHistory.scrollHeight;
        }
    }
    
    finishStreaming() {
        this.isStreaming = false;
        this.currentAssistantMessage = null;
        this.setLoading(false);
    }
    
    addMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const roleLabel = document.createElement('div');
        roleLabel.className = 'role';
        roleLabel.textContent = role === 'user' ? 'You' : 'Axiom';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'content';
        contentDiv.textContent = content;
        
        messageDiv.appendChild(roleLabel);
        messageDiv.appendChild(contentDiv);
        
        this.chatHistory.appendChild(messageDiv);
        this.chatHistory.scrollTop = this.chatHistory.scrollHeight;
        
        return messageDiv;
    }
    
    renderConversation(messages) {
        this.chatHistory.innerHTML = '';
        messages.forEach(msg => {
            this.addMessage(msg.role, msg.content);
        });
    }
    
    setLoading(loading) {
        this.sendBtn.disabled = loading || !this.isConnected;
        this.messageInput.disabled = loading;
        this.stopBtn.disabled = !loading || !this.isStreaming;
        this.sendBtn.textContent = loading ? 'Sending...' : 'Send';
    }
    
    setStatus(message, type = 'info') {
        this.status.textContent = message;
        this.status.className = `status ${type}`;
        
        if (type !== 'error') {
            setTimeout(() => {
                this.status.textContent = '';
                this.status.className = 'status';
            }, 3000);
        }
    }
}

// Initialize chat when page loads
document.addEventListener('DOMContentLoaded', () => {
    new AxiomChat();
});