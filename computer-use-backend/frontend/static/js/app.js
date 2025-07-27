/**
 * Computer Use Agent Frontend Application
 */
class ComputerUseApp {
    constructor() {
        this.baseUrl = window.location.protocol + '//' + window.location.host;
        this.apiUrl = this.baseUrl + '/api';
        this.wsUrl = this.baseUrl.replace('http', 'ws') + '/api/ws';
        
        this.currentSession = null;
        this.websocket = null;
        
        this.initializeElements();
        this.setupEventListeners();
        this.loadSessions();
    }
    
    initializeElements() {
        // Get DOM elements
        this.elements = {
            // Status indicators
            connectionStatus: document.getElementById('connection-status'),
            connectionText: document.getElementById('connection-text'),
            
            // Session management
            newSessionBtn: document.getElementById('new-session-btn'),
            sessionList: document.getElementById('session-list'),
            currentSessionName: document.getElementById('current-session-name'),
            
            // Chat interface
            chatMessages: document.getElementById('chat-messages'),
            messageInput: document.getElementById('message-input'),
            sendBtn: document.getElementById('send-btn'),
            
            // VNC
            vncConnectBtn: document.getElementById('vnc-connect-btn'),
            vncContainer: document.getElementById('vnc-container'),
            vncStatus: document.getElementById('vnc-status'),
            
            // Modal
            modal: document.getElementById('new-session-modal'),
            closeModal: document.getElementById('close-modal'),
            sessionNameInput: document.getElementById('session-name-input'),
            createSessionBtn: document.getElementById('create-session-btn'),
            cancelSessionBtn: document.getElementById('cancel-session-btn'),
            
            // File management
            fileDropZone: document.getElementById('file-drop-zone'),
            fileInput: document.getElementById('file-input')
        };
    }
    
    setupEventListeners() {
        // Session management
        this.elements.newSessionBtn.addEventListener('click', () => this.showNewSessionModal());
        this.elements.createSessionBtn.addEventListener('click', () => this.createSession());
        this.elements.cancelSessionBtn.addEventListener('click', () => this.hideNewSessionModal());
        this.elements.closeModal.addEventListener('click', () => this.hideNewSessionModal());
        
        // Chat
        this.elements.sendBtn.addEventListener('click', () => this.sendMessage());
        this.elements.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // VNC
        this.elements.vncConnectBtn.addEventListener('click', () => {
            this.connectVNC();
        });
        
        // File handling
        this.elements.fileDropZone.addEventListener('click', () => this.elements.fileInput.click());
        this.elements.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        
        // Modal outside click
        window.addEventListener('click', (e) => {
            if (e.target === this.elements.modal) {
                this.hideNewSessionModal();
            }
        });
        
        // Drag and drop
        this.setupDragAndDrop();
        
        // Auto-connect VNC when page loads
        this.connectVNC();
    }
    
    setupDragAndDrop() {
        const dropZone = this.elements.fileDropZone;
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });
        
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'));
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'));
        });
        
        dropZone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            this.handleFiles(files);
        });
    }
    
    async loadSessions() {
        try {
            const response = await fetch(`${this.apiUrl}/sessions`);
            const sessions = await response.json();
            
            this.renderSessions(sessions);
        } catch (error) {
            console.error('Error loading sessions:', error);
            this.showError('Failed to load sessions');
        }
    }
    
    renderSessions(sessions) {
        const sessionList = this.elements.sessionList;
        
        if (sessions.length === 0) {
            sessionList.innerHTML = '<div class="session-item">No sessions yet. Create your first task!</div>';
            return;
        }
        
        sessionList.innerHTML = sessions.map(session => `
            <div class="session-item" data-session-id="${session.id}">
                <div class="session-name">${session.name}</div>
                <div class="session-info">
                    ${session.message_count} messages • ${session.status} • ${new Date(session.created_at).toLocaleDateString()}
                </div>
            </div>
        `).join('');
        
        // Add click listeners
        sessionList.querySelectorAll('.session-item').forEach(item => {
            item.addEventListener('click', () => {
                const sessionId = item.dataset.sessionId;
                this.selectSession(sessionId);
            });
        });
    }
    
    async selectSession(sessionId) {
        try {
            // Update UI
            document.querySelectorAll('.session-item').forEach(item => {
                item.classList.remove('active');
            });
            document.querySelector(`[data-session-id="${sessionId}"]`).classList.add('active');
            
            // Get session details
            const response = await fetch(`${this.apiUrl}/sessions/${sessionId}`);
            const session = await response.json();
            
            this.currentSession = session;
            this.elements.currentSessionName.textContent = session.name;
            
            // Enable chat input
            this.elements.messageInput.disabled = false;
            this.elements.sendBtn.disabled = false;
            
            // Load messages
            this.renderMessages(session.messages);
            
            // Connect WebSocket
            this.connectWebSocket(sessionId);
            
        } catch (error) {
            console.error('Error selecting session:', error);
            this.showError('Failed to load session');
        }
    }
    
    renderMessages(messages) {
        const chatMessages = this.elements.chatMessages;
        
        if (messages.length === 0) {
            chatMessages.innerHTML = '<div class="welcome-message"><p>Session is ready! Send a message to start interacting with the agent.</p></div>';
            return;
        }
        
        chatMessages.innerHTML = messages.map(message => `
            <div class="message ${message.role}">
                <div class="message-header">
                    <span>${message.role}</span>
                    <span>${new Date(message.timestamp).toLocaleTimeString()}</span>
                </div>
                <div class="message-content">${this.formatMessageContent(message.content)}</div>
            </div>
        `).join('');
        
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    formatMessageContent(content) {
        // Basic HTML escaping and formatting
        return content
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/\n/g, '<br>');
    }
    
    connectWebSocket(sessionId) {
        // Close existing connection
        if (this.websocket) {
            this.websocket.close();
        }
        
        try {
            this.websocket = new WebSocket(`${this.wsUrl}/${sessionId}`);
            
            this.websocket.onopen = () => {
                console.log('WebSocket connected');
                this.updateConnectionStatus(true);
            };
            
            this.websocket.onmessage = (event) => {
                const message = JSON.parse(event.data);
                this.handleWebSocketMessage(message);
            };
            
            this.websocket.onclose = () => {
                console.log('WebSocket disconnected');
                this.updateConnectionStatus(false);
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus(false);
            };
            
        } catch (error) {
            console.error('Error connecting WebSocket:', error);
            this.updateConnectionStatus(false);
        }
    }
    
    handleWebSocketMessage(message) {
        const chatMessages = this.elements.chatMessages;
        
        switch (message.type) {
            case 'agent_progress':
                this.addProgressMessage(message.message, message.step);
                break;
                
            case 'tool_execution':
                this.addToolExecutionMessage(message);
                break;
                
            case 'agent_response':
                this.addAgentMessage(message.content);
                break;
                
            case 'error':
                this.showError(message.data.message);
                break;
                
            default:
                console.log('Unknown WebSocket message:', message);
        }
    }
    
    addProgressMessage(message, step) {
        const chatMessages = this.elements.chatMessages;
        const progressDiv = document.createElement('div');
        progressDiv.className = 'progress-message';
        progressDiv.innerHTML = `<strong>${step || 'Progress'}:</strong> ${this.formatMessageContent(message)}`;
        
        chatMessages.appendChild(progressDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    addToolExecutionMessage(message) {
        const chatMessages = this.elements.chatMessages;
        const toolDiv = document.createElement('div');
        toolDiv.className = 'tool-execution';
        toolDiv.innerHTML = `
            <strong>Tool: ${message.tool_name}</strong><br>
            Status: ${message.status}<br>
            ${message.tool_output?.output ? `Output: ${this.formatMessageContent(message.tool_output.output)}` : ''}
        `;
        
        chatMessages.appendChild(toolDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    addAgentMessage(content) {
        const chatMessages = this.elements.chatMessages;
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant';
        messageDiv.innerHTML = `
            <div class="message-header">
                <span>assistant</span>
                <span>${new Date().toLocaleTimeString()}</span>
            </div>
            <div class="message-content">${this.formatMessageContent(content)}</div>
        `;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    updateConnectionStatus(connected) {
        const status = this.elements.connectionStatus;
        const text = this.elements.connectionText;
        
        if (connected) {
            status.classList.remove('offline');
            status.classList.add('online');
            text.textContent = 'Connected';
        } else {
            status.classList.remove('online');
            status.classList.add('offline');
            text.textContent = 'Disconnected';
        }
    }
    
    showNewSessionModal() {
        this.elements.modal.style.display = 'block';
        this.elements.sessionNameInput.focus();
    }
    
    hideNewSessionModal() {
        this.elements.modal.style.display = 'none';
        this.elements.sessionNameInput.value = '';
    }
    
    async createSession() {
        const name = this.elements.sessionNameInput.value.trim();
        
        if (!name) {
            alert('Please enter a session name');
            return;
        }
        
        try {
            const response = await fetch(`${this.apiUrl}/sessions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name })
            });
            
            if (!response.ok) {
                throw new Error('Failed to create session');
            }
            
            const session = await response.json();
            
            // Hide modal
            this.hideNewSessionModal();
            
            // Reload sessions
            await this.loadSessions();
            
            // Select new session
            await this.selectSession(session.id);
            
        } catch (error) {
            console.error('Error creating session:', error);
            this.showError('Failed to create session');
        }
    }
    
    async sendMessage() {
        const message = this.elements.messageInput.value.trim();
        
        if (!message || !this.currentSession) {
            return;
        }
        
        // Disable input temporarily
        this.elements.messageInput.disabled = true;
        this.elements.sendBtn.disabled = true;
        
        try {
            // Add user message to chat immediately
            this.addUserMessage(message);
            
            // Clear input
            this.elements.messageInput.value = '';
            
            // Send message to API
            const response = await fetch(`${this.apiUrl}/sessions/${this.currentSession.id}/messages`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ content: message })
            });
            
            if (!response.ok) {
                throw new Error('Failed to send message');
            }
            
            // Add processing indicator
            this.addProgressMessage('Processing your request...', 'system');
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.showError('Failed to send message');
        } finally {
            // Re-enable input
            this.elements.messageInput.disabled = false;
            this.elements.sendBtn.disabled = false;
            this.elements.messageInput.focus();
        }
    }
    
    addUserMessage(content) {
        const chatMessages = this.elements.chatMessages;
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user';
        messageDiv.innerHTML = `
            <div class="message-header">
                <span>user</span>
                <span>${new Date().toLocaleTimeString()}</span>
            </div>
            <div class="message-content">${this.formatMessageContent(content)}</div>
        `;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    connectVNC() {
        this.elements.vncStatus.textContent = 'VNC: Connecting...';
        
        // Connect to the working noVNC interface on port 6080
        this.elements.vncContainer.innerHTML = `
            <iframe 
                id="vnc-iframe"
                src="http://localhost:6080/vnc.html?autoconnect=1&resize=scale&view_only=0&reconnect=1&reconnect_delay=2000"
                style="width: 100%; height: 100%; border: none; border-radius: 8px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);"
                allowfullscreen
            ></iframe>
        `;
        
        this.elements.vncStatus.textContent = 'VNC: Connected (noVNC on port 6080)';
        
        // Add VNC controls
        this.addVNCControls();
    }
    
    addVNCControls() {
        const controlsDiv = document.createElement('div');
        controlsDiv.className = 'vnc-controls-panel';
        controlsDiv.innerHTML = `
            <button id="toggle-view-only" class="btn btn-secondary">Toggle Control</button>
            <button id="reconnect-vnc" class="btn btn-secondary">Reconnect</button>
            <button id="fullscreen-vnc" class="btn btn-secondary">Fullscreen</button>
        `;
        
        this.elements.vncContainer.appendChild(controlsDiv);
        
        // Add event listeners
        document.getElementById('toggle-view-only').addEventListener('click', () => {
            const iframe = document.getElementById('vnc-iframe');
            const currentSrc = iframe.src;
            if (currentSrc.includes('view_only=1')) {
                iframe.src = currentSrc.replace('view_only=1', 'view_only=0');
                document.getElementById('toggle-view-only').textContent = 'View Only';
            } else {
                iframe.src = currentSrc.replace('view_only=0', 'view_only=1');
                document.getElementById('toggle-view-only').textContent = 'Interactive';
            }
        });
        
        document.getElementById('reconnect-vnc').addEventListener('click', () => {
            const iframe = document.getElementById('vnc-iframe');
            iframe.src = iframe.src;
        });
        
        document.getElementById('fullscreen-vnc').addEventListener('click', () => {
            const iframe = document.getElementById('vnc-iframe');
            if (iframe.requestFullscreen) {
                iframe.requestFullscreen();
            } else if (iframe.webkitRequestFullscreen) {
                iframe.webkitRequestFullscreen();
            } else if (iframe.msRequestFullscreen) {
                iframe.msRequestFullscreen();
            }
        });
    }
    
    handleFileSelect(event) {
        const files = event.target.files;
        this.handleFiles(files);
    }
    
    handleFiles(files) {
        // Placeholder for file handling
        console.log('Files selected:', files);
        this.showInfo(`${files.length} file(s) selected (file handling not implemented in demo)`);
    }
    
    showError(message) {
        // Simple error display - in production, use a proper notification system
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        
        document.body.appendChild(errorDiv);
        
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }
    
    showInfo(message) {
        // Simple info display
        const infoDiv = document.createElement('div');
        infoDiv.className = 'progress-message';
        infoDiv.textContent = message;
        
        document.body.appendChild(infoDiv);
        
        setTimeout(() => {
            infoDiv.remove();
        }, 3000);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ComputerUseApp();
}); 