"""
Document Viewer Web Interface
Provides a web UI to browse and view documents
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from typing import Optional

from ...memory.persistent_memory_manager import persistent_memory
from ..dependencies import get_current_user

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def document_viewer(request: Request):
    """
    Main document viewer interface
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LexOS Document Vault</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #0a0a0a;
                color: #e0e0e0;
                height: 100vh;
                overflow: hidden;
            }
            
            .container {
                display: flex;
                height: 100vh;
            }
            
            .sidebar {
                width: 300px;
                background: #1a1a1a;
                border-right: 1px solid #333;
                overflow-y: auto;
                padding: 20px;
            }
            
            .main {
                flex: 1;
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            
            .header {
                background: #1a1a1a;
                padding: 20px;
                border-bottom: 1px solid #333;
            }
            
            .content {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
            }
            
            h1 {
                font-size: 24px;
                margin-bottom: 10px;
                color: #00ff88;
            }
            
            .search-box {
                width: 100%;
                padding: 10px;
                background: #2a2a2a;
                border: 1px solid #444;
                border-radius: 5px;
                color: #e0e0e0;
                margin-bottom: 20px;
                font-size: 14px;
            }
            
            .document-list {
                list-style: none;
            }
            
            .document-item {
                padding: 12px;
                margin-bottom: 8px;
                background: #2a2a2a;
                border-radius: 5px;
                cursor: pointer;
                transition: all 0.2s;
                border: 1px solid transparent;
            }
            
            .document-item:hover {
                background: #333;
                border-color: #00ff88;
            }
            
            .document-item.active {
                background: #333;
                border-color: #00ff88;
            }
            
            .document-name {
                font-weight: 500;
                margin-bottom: 4px;
                color: #fff;
            }
            
            .document-meta {
                font-size: 12px;
                color: #888;
            }
            
            .preview-container {
                background: #1a1a1a;
                border-radius: 8px;
                padding: 20px;
                height: 100%;
                overflow: auto;
            }
            
            .preview-text {
                white-space: pre-wrap;
                line-height: 1.6;
                font-family: 'Monaco', 'Consolas', monospace;
                font-size: 14px;
            }
            
            .preview-image {
                max-width: 100%;
                max-height: 600px;
                display: block;
                margin: 0 auto;
                border-radius: 8px;
            }
            
            .empty-state {
                text-align: center;
                color: #666;
                padding: 40px;
            }
            
            .loading {
                text-align: center;
                padding: 40px;
                color: #00ff88;
            }
            
            .error {
                background: #2a1a1a;
                border: 1px solid #ff4444;
                padding: 20px;
                border-radius: 8px;
                color: #ff6666;
            }
            
            .stats {
                background: #2a2a2a;
                padding: 15px;
                border-radius: 5px;
                margin-top: 20px;
                font-size: 12px;
            }
            
            .stat-item {
                display: flex;
                justify-content: space-between;
                margin-bottom: 8px;
            }
            
            .stat-label {
                color: #888;
            }
            
            .stat-value {
                color: #00ff88;
                font-weight: 500;
            }
            
            .btn {
                display: inline-block;
                padding: 8px 16px;
                background: #00ff88;
                color: #000;
                text-decoration: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: 500;
                transition: all 0.2s;
                margin-right: 10px;
            }
            
            .btn:hover {
                background: #00cc66;
                transform: translateY(-1px);
            }
            
            .btn-secondary {
                background: #444;
                color: #e0e0e0;
            }
            
            .btn-secondary:hover {
                background: #555;
            }
            
            .document-actions {
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid #333;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="sidebar">
                <h1>Document Vault</h1>
                <input type="text" class="search-box" placeholder="Search documents..." id="searchBox">
                
                <ul class="document-list" id="documentList">
                    <li class="loading">Loading documents...</li>
                </ul>
                
                <div class="stats" id="stats">
                    <div class="stat-item">
                        <span class="stat-label">Total Documents:</span>
                        <span class="stat-value" id="totalDocs">-</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Storage Used:</span>
                        <span class="stat-value" id="storageUsed">-</span>
                    </div>
                </div>
            </div>
            
            <div class="main">
                <div class="header">
                    <h2 id="documentTitle">Select a document</h2>
                    <div class="document-actions" id="documentActions" style="display: none;">
                        <a href="#" class="btn" id="viewBtn">View Full</a>
                        <a href="#" class="btn btn-secondary" id="downloadBtn">Download</a>
                    </div>
                </div>
                <div class="content">
                    <div class="preview-container" id="previewContainer">
                        <div class="empty-state">
                            Select a document from the list to preview
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            let documents = [];
            let currentDoc = null;
            
            // Load documents on page load
            async function loadDocuments() {
                try {
                    const response = await fetch('/api/v1/documents/list?limit=100');
                    const data = await response.json();
                    
                    if (data.success) {
                        documents = data.documents;
                        renderDocumentList();
                        loadStats();
                    }
                } catch (error) {
                    console.error('Failed to load documents:', error);
                }
            }
            
            // Load storage stats
            async function loadStats() {
                try {
                    const response = await fetch('/api/v1/documents/stats');
                    const data = await response.json();
                    
                    if (data.success) {
                        document.getElementById('totalDocs').textContent = data.stats.documents_stored || 0;
                        document.getElementById('storageUsed').textContent = 
                            `${(data.stats.total_storage_mb || 0).toFixed(1)} MB`;
                    }
                } catch (error) {
                    console.error('Failed to load stats:', error);
                }
            }
            
            // Render document list
            function renderDocumentList(filter = '') {
                const list = document.getElementById('documentList');
                const filtered = documents.filter(doc => 
                    doc.original_name.toLowerCase().includes(filter.toLowerCase())
                );
                
                if (filtered.length === 0) {
                    list.innerHTML = '<li class="empty-state">No documents found</li>';
                    return;
                }
                
                list.innerHTML = filtered.map(doc => `
                    <li class="document-item" onclick="selectDocument('${doc.doc_id}')">
                        <div class="document-name">${doc.original_name}</div>
                        <div class="document-meta">
                            ${doc.file_type} • ${formatFileSize(doc.size)} • ${formatDate(doc.created_at)}
                        </div>
                    </li>
                `).join('');
            }
            
            // Select and preview document
            async function selectDocument(docId) {
                // Update active state
                document.querySelectorAll('.document-item').forEach(item => {
                    item.classList.remove('active');
                });
                event.target.closest('.document-item').classList.add('active');
                
                // Load preview
                const container = document.getElementById('previewContainer');
                container.innerHTML = '<div class="loading">Loading preview...</div>';
                
                try {
                    const response = await fetch(`/api/v1/documents/preview/${docId}`);
                    const data = await response.json();
                    
                    currentDoc = data;
                    document.getElementById('documentTitle').textContent = data.name;
                    document.getElementById('documentActions').style.display = 'block';
                    
                    // Update action buttons
                    document.getElementById('viewBtn').href = `/api/v1/documents/view/${docId}`;
                    document.getElementById('downloadBtn').href = `/api/v1/documents/download/${docId}`;
                    
                    // Render preview
                    if (data.preview.type === 'text') {
                        container.innerHTML = `<div class="preview-text">${escapeHtml(data.preview.data)}</div>`;
                    } else if (data.preview.type === 'image') {
                        container.innerHTML = `<img src="${data.preview.data}" class="preview-image" alt="${data.name}">`;
                    } else {
                        container.innerHTML = `<div class="empty-state">${data.preview.message || 'No preview available'}</div>`;
                    }
                } catch (error) {
                    container.innerHTML = '<div class="error">Failed to load preview</div>';
                }
            }
            
            // Helper functions
            function formatFileSize(bytes) {
                if (bytes < 1024) return bytes + ' B';
                if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
                return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
            }
            
            function formatDate(dateStr) {
                const date = new Date(dateStr);
                return date.toLocaleDateString();
            }
            
            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
            
            // Search functionality
            document.getElementById('searchBox').addEventListener('input', (e) => {
                renderDocumentList(e.target.value);
            });
            
            // Initialize
            loadDocuments();
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)