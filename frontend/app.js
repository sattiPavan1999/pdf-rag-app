const API_BASE = "http://localhost:8000";

// ===== State Management =====
let conversationHistory = [];
let uploadedPDFs = [];

// ===== Initialize App =====
document.addEventListener('DOMContentLoaded', () => {
  initializeApp();
});

function initializeApp() {
  // Load conversation history from localStorage
  loadConversationHistory();
  loadUploadedPDFs();
  
  // Setup event listeners
  setupEventListeners();
  
  // Render initial state
  renderConversation();
  renderPDFList();
}

// ===== Event Listeners =====
function setupEventListeners() {
  const uploadArea = document.getElementById('uploadArea');
  const fileInput = document.getElementById('pdfFile');
  const questionInput = document.getElementById('questionInput');
  
  // Upload area click
  uploadArea.addEventListener('click', () => fileInput.click());
  
  // Drag and drop
  uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
  });
  
  uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
  });
  
  uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0 && files[0].type === 'application/pdf') {
      fileInput.files = files;
      showStatus('File selected: ' + files[0].name, 'success');
    } else {
      showStatus('Please drop a PDF file', 'error');
    }
  });
  
  // Enter key to send message
  questionInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      askQuestion();
    }
  });
}

// ===== PDF Upload =====
async function uploadPDF() {
  const fileInput = document.getElementById('pdfFile');
  const uploadBtn = document.getElementById('uploadBtn');
  
  if (!fileInput.files.length) {
    showStatus('Please select a PDF file', 'error');
    return;
  }
  
  const file = fileInput.files[0];
  const formData = new FormData();
  formData.append('file', file);
  
  // Show loading
  showLoading(true);
  uploadBtn.disabled = true;
  
  try {
    const res = await fetch(`${API_BASE}/upload-pdf`, {
      method: 'POST',
      body: formData
    });
    
    if (!res.ok) throw new Error('Upload failed');
    
    const data = await res.json();
    
    // Add to uploaded PDFs list
    const pdfInfo = {
      name: file.name,
      size: formatFileSize(file.size),
      uploadedAt: new Date().toISOString()
    };
    
    uploadedPDFs.push(pdfInfo);
    saveUploadedPDFs();
    renderPDFList();
    
    // Clear conversation when new PDF is uploaded
    conversationHistory = [];
    saveConversationHistory();
    renderConversation();
    
    showStatus('✅ PDF uploaded and processed successfully!', 'success');
    fileInput.value = '';
    
  } catch (err) {
    console.error('Upload error:', err);
    showStatus('❌ Upload failed. Please try again.', 'error');
  } finally {
    showLoading(false);
    uploadBtn.disabled = false;
  }
}

// ===== Chat Functions =====
async function askQuestion() {
  const input = document.getElementById('questionInput');
  const sendBtn = document.getElementById('sendBtn');
  const question = input.value.trim();
  
  if (!question) return;
  
  // Check if PDF is uploaded
  if (uploadedPDFs.length === 0) {
    showStatus('Please upload a PDF first', 'error');
    return;
  }
  
  // Add user message to conversation
  const userMessage = {
    role: 'user',
    content: question,
    timestamp: new Date().toISOString()
  };
  
  conversationHistory.push(userMessage);
  saveConversationHistory();
  renderConversation();
  
  // Clear input
  input.value = '';
  sendBtn.disabled = true;
  
  // Show typing indicator
  showTypingIndicator();
  
  try {
    const res = await fetch(`${API_BASE}/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });
    
    if (!res.ok) throw new Error('Failed to get response');
    
    const data = await res.json();
    
    // Remove typing indicator
    removeTypingIndicator();
    
    // Add bot response to conversation
    const botMessage = {
      role: 'bot',
      content: data.answer,
      timestamp: new Date().toISOString()
    };
    
    conversationHistory.push(botMessage);
    saveConversationHistory();
    renderConversation();
    
  } catch (err) {
    console.error('Chat error:', err);
    removeTypingIndicator();
    
    const errorMessage = {
      role: 'bot',
      content: '❌ Sorry, I encountered an error. Please try again.',
      timestamp: new Date().toISOString()
    };
    
    conversationHistory.push(errorMessage);
    saveConversationHistory();
    renderConversation();
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
}

function clearChat() {
  if (conversationHistory.length === 0) return;
  
  if (confirm('Are you sure you want to clear the conversation history?')) {
    conversationHistory = [];
    saveConversationHistory();
    renderConversation();
    showStatus('Conversation cleared', 'success');
  }
}

// ===== Rendering Functions =====
function renderConversation() {
  const chatBox = document.getElementById('chatBox');
  
  if (conversationHistory.length === 0) {
    chatBox.innerHTML = `
      <div class="welcome-message">
        <svg class="welcome-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <h3>Welcome to PDF Chat Agent!</h3>
        <p>Upload a PDF document to get started. Once uploaded, you can ask questions about the content and I'll provide answers based on the document.</p>
      </div>
    `;
    return;
  }
  
  chatBox.innerHTML = conversationHistory.map(msg => {
    const isUser = msg.role === 'user';
    const avatarIcon = isUser 
      ? '<path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2M12 11a4 4 0 100-8 4 4 0 000 8z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
      : '<path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>';
    
    return `
      <div class="message ${msg.role}">
        <div class="message-avatar">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            ${avatarIcon}
          </svg>
        </div>
        <div class="message-content">
          <div class="message-text">${escapeHtml(msg.content)}</div>
        </div>
      </div>
    `;
  }).join('');
  
  // Scroll to bottom
  chatBox.scrollTop = chatBox.scrollHeight;
}

function showTypingIndicator() {
  const chatBox = document.getElementById('chatBox');
  const indicator = document.createElement('div');
  indicator.id = 'typingIndicator';
  indicator.className = 'message bot';
  indicator.innerHTML = `
    <div class="message-avatar">
      <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
    <div class="message-content">
      <div class="typing-indicator">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    </div>
  `;
  chatBox.appendChild(indicator);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function removeTypingIndicator() {
  const indicator = document.getElementById('typingIndicator');
  if (indicator) indicator.remove();
}

function renderPDFList() {
  const pdfItems = document.getElementById('pdfItems');
  
  if (uploadedPDFs.length === 0) {
    pdfItems.innerHTML = '<p class="empty-state">No documents uploaded yet</p>';
    return;
  }
  
  pdfItems.innerHTML = uploadedPDFs.map((pdf, index) => `
    <div class="pdf-item">
      <div class="pdf-item-info">
        <svg class="pdf-item-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <div>
          <div class="pdf-item-name" title="${pdf.name}">${pdf.name}</div>
        </div>
      </div>
      <button class="pdf-item-delete" onclick="deletePDF(${index})" title="Delete">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2M10 11v6M14 11v6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>
  `).join('');
}

function deletePDF(index) {
  if (confirm('Are you sure you want to remove this PDF?')) {
    uploadedPDFs.splice(index, 1);
    saveUploadedPDFs();
    renderPDFList();
    
    // Clear conversation when PDF is deleted
    if (uploadedPDFs.length === 0) {
      conversationHistory = [];
      saveConversationHistory();
      renderConversation();
    }
    
    showStatus('PDF removed', 'success');
  }
}

// ===== UI Helper Functions =====
function showStatus(message, type = 'loading') {
  const statusEl = document.getElementById('uploadStatus');
  statusEl.textContent = message;
  statusEl.className = `status-message ${type} show`;
  
  setTimeout(() => {
    statusEl.classList.remove('show');
  }, 3000);
}

function showLoading(show) {
  const overlay = document.getElementById('loadingOverlay');
  if (show) {
    overlay.classList.add('show');
  } else {
    overlay.classList.remove('show');
  }
}

// ===== LocalStorage Functions =====
function saveConversationHistory() {
  localStorage.setItem('pdfChatHistory', JSON.stringify(conversationHistory));
}

function loadConversationHistory() {
  const saved = localStorage.getItem('pdfChatHistory');
  if (saved) {
    try {
      conversationHistory = JSON.parse(saved);
    } catch (e) {
      console.error('Failed to load conversation history:', e);
      conversationHistory = [];
    }
  }
}

function saveUploadedPDFs() {
  localStorage.setItem('uploadedPDFs', JSON.stringify(uploadedPDFs));
}

function loadUploadedPDFs() {
  const saved = localStorage.getItem('uploadedPDFs');
  if (saved) {
    try {
      uploadedPDFs = JSON.parse(saved);
    } catch (e) {
      console.error('Failed to load uploaded PDFs:', e);
      uploadedPDFs = [];
    }
  }
}

// ===== Utility Functions =====
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}
