// ===== State Management =====
let currentView = 'chat';
let currentConversation = null;
let documents = [];
let conversations = [];

// ===== DOM Elements =====
const navBtns = document.querySelectorAll('.nav-btn');
const views = document.querySelectorAll('.view');
const chatView = document.getElementById('chatView');
const documentsView = document.getElementById('documentsView');
const chatContainer = document.getElementById('chatContainer');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const fileInput = document.getElementById('fileInput');
const uploadZone = document.getElementById('uploadZone');
const documentsGrid = document.getElementById('documentsGrid');
const conversationsList = document.getElementById('conversationsList');
const newConversationBtn = document.getElementById('newConversationBtn');
const toast = document.getElementById('toast');
const loadingOverlay = document.getElementById('loadingOverlay');

// ===== API Base URL =====
const API_BASE = '/api';

// ===== Initialization =====
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
});

async function initializeApp() {
    await loadDocuments();
    await loadConversations();
}

function setupEventListeners() {
    // Navigation
    navBtns.forEach(btn => {
        btn.addEventListener('click', () => switchView(btn.dataset.view));
    });

    // Chat
    messageInput.addEventListener('input', handleInputChange);
    messageInput.addEventListener('keydown', handleKeyDown);
    sendButton.addEventListener('click', sendMessage);

    // Documents
    fileInput.addEventListener('change', handleFileSelect);
    uploadZone.addEventListener('click', () => fileInput.click());
    uploadZone.addEventListener('dragover', handleDragOver);
    uploadZone.addEventListener('dragleave', handleDragLeave);
    uploadZone.addEventListener('drop', handleDrop);

    // Conversations
    newConversationBtn.addEventListener('click', createNewConversation);
}

// ===== View Management =====
function switchView(viewName) {
    currentView = viewName;

    // Update nav
    navBtns.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.view === viewName);
    });

    // Update views
    views.forEach(view => {
        view.classList.toggle('active', view.id === `${viewName}View`);
    });
}

// ===== Documents =====
async function loadDocuments() {
    try {
        const response = await fetch(`${API_BASE}/documents`);
        const data = await response.json();
        documents = data.documents || [];
        renderDocuments();
    } catch (error) {
        console.error('Load documents error:', error);
    }
}

function renderDocuments() {
    if (documents.length === 0) {
        documentsGrid.innerHTML = '<div class="empty-state">Chưa có tài liệu nào được tải lên</div>';
        return;
    }

    documentsGrid.innerHTML = documents.map(doc => `
        <div class="document-card" data-doc-id="${doc.doc_id}">
            <div class="document-header">
                <div class="document-icon">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                        <polyline points="14 2 14 8 20 8"/>
                    </svg>
                </div>
                <button class="btn-icon" onclick="deleteDocument('${doc.doc_id}')" title="Xóa">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                    </svg>
                </button>
            </div>
            <div class="document-name">${doc.filename}</div>
            <div class="document-meta">${doc.chunks_count} chunks • ${formatFileSize(doc.file_size)}</div>
        </div>
    `).join('');
}

function handleDragOver(e) {
    e.preventDefault();
    uploadZone.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');
    const files = Array.from(e.dataTransfer.files);
    uploadFiles(files);
}

function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    uploadFiles(files);
    fileInput.value = '';
}

async function uploadFiles(files) {
    if (files.length === 0) return;

    showLoading(true);

    try {
        for (const file of files) {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(`${API_BASE}/documents/upload`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Upload failed');
            }
        }

        showToast(`✅ Đã tải lên ${files.length} tệp thành công`, 'success');
        await loadDocuments();

    } catch (error) {
        console.error('Upload error:', error);
        showToast(`❌ Error: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

async function deleteDocument(docId) {
    if (!confirm('Bạn có chắc chắn muốn xóa tài liệu này không?')) return;

    showLoading(true);

    try {
        const response = await fetch(`${API_BASE}/documents/${docId}`, {
            method: 'DELETE'
        });

        if (!response.ok) throw new Error('Delete failed');

        showToast('🗑️ Đã xóa tài liệu', 'success');
        await loadDocuments();

    } catch (error) {
        console.error('Delete error:', error);
        showToast(`❌ Error: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// ===== Conversations =====
async function loadConversations() {
    try {
        const response = await fetch(`${API_BASE}/conversations`);
        const data = await response.json();
        conversations = data.conversations || [];
        renderConversations();
    } catch (error) {
        console.error('Load conversations error:', error);
    }
}

function renderConversations() {
    if (conversations.length === 0) {
        conversationsList.innerHTML = '<div class="empty-state">Chưa có cuộc trò chuyện nào</div>';
        return;
    }

    conversationsList.innerHTML = conversations.map(conv => `
        <div class="conversation-item ${currentConversation?.id === conv.id ? 'active' : ''}" 
             onclick="loadConversation('${conv.id}')">
            <div class="conversation-title">${conv.title}</div>
            <div class="conversation-meta">${conv.message_count} messages</div>
        </div>
    `).join('');
}

async function createNewConversation() {
    try {
        const response = await fetch(`${API_BASE}/conversations`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: 'Cuộc trò chuyện mới' })
        });

        const conversation = await response.json();
        currentConversation = conversation;

        // Clear chat
        const welcome = chatContainer.querySelector('.welcome');
        if (welcome) welcome.remove();

        await loadConversations();
        switchView('chat');

    } catch (error) {
        console.error('Create conversation error:', error);
    }
}

async function loadConversation(conversationId) {
    try {
        const response = await fetch(`${API_BASE}/conversations/${conversationId}`);
        currentConversation = await response.json();

        // Clear and render messages
        chatContainer.innerHTML = '';
        currentConversation.messages.forEach(msg => {
            addMessageToUI(msg.role, msg.content, msg.sources);
        });

        renderConversations();

    } catch (error) {
        console.error('Load conversation error:', error);
    }
}

// ===== Chat =====
function handleInputChange() {
    const hasText = messageInput.value.trim().length > 0;
    sendButton.disabled = !hasText;

    // Auto-resize
    messageInput.style.height = 'auto';
    messageInput.style.height = messageInput.scrollHeight + 'px';
}

function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
}

async function sendMessage() {
    const question = messageInput.value.trim();
    if (!question) return;

    // Clear input
    messageInput.value = '';
    messageInput.style.height = 'auto';
    sendButton.disabled = true;

    // Remove welcome if exists
    const welcome = chatContainer.querySelector('.welcome');
    if (welcome) welcome.remove();

    // Add user message
    addMessageToUI('user', question);

    // Show loading
    const loadingMsg = addMessageToUI('assistant', '🤔 Đang suy nghĩ...', [], true);

    try {
        const response = await fetch(`${API_BASE}/chat/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question,
                conversation_id: currentConversation?.id,
                k: 5
            })
        });

        const data = await response.json();

        // Remove loading
        loadingMsg.remove();

        // Check for error response
        if (!response.ok) {
            throw new Error(data.detail || 'Query failed');
        }

        // Add assistant message
        const sources = (data.sources || []).map(s => s.filename);
        addMessageToUI('assistant', data.answer, sources);

        // Update conversation
        if (data.conversation_id && !currentConversation) {
            await loadConversations();
        }

    } catch (error) {
        console.error('Query error:', error);
        loadingMsg.remove();
        addMessageToUI('assistant', `❌ Lỗi: ${error.message}`);
    }
}

function addMessageToUI(role, content, sources = [], isTemp = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    if (isTemp) messageDiv.dataset.temp = 'true';

    const avatar = role === 'user' ? '👤' : '🤖';

    let sourcesHTML = '';
    if (sources && sources.length > 0) {
        sourcesHTML = `
            <div class="message-sources">
                <div style="font-size: 0.875rem; font-weight: 600; margin-bottom: 0.5rem;">Nguồn tham khảo:</div>
                ${sources.map(s => `<span class="source-tag">${s}</span>`).join('')}
            </div>
        `;
    }

    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <div class="message-bubble">
                ${content.replace(/\n/g, '<br>')}
                ${sourcesHTML}
            </div>
        </div>
    `;

    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    return messageDiv;
}

// ===== Utilities =====
function showToast(message, type = 'success') {
    toast.textContent = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function showLoading(show) {
    loadingOverlay.classList.toggle('show', show);
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}
