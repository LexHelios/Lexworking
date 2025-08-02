# LexOS Document Viewer - Access From Anywhere

## Overview

The LexOS Document Vault is now accessible from anywhere through multiple interfaces:

## 1. Web Interface (Browser Access)

### Simple Viewer
Access at: `http://your-server:8000/vault/`

This provides a clean, simple interface to:
- View all stored documents
- Search and filter by type
- Preview documents inline
- Download files

### Full Document Manager
Access at: `http://your-server:8000/vault.html`

This provides a richer interface with:
- Split-panel view (document list + preview)
- Drag-and-drop upload
- Real-time search
- File type filtering
- Inline viewing for PDFs, images, and text

## 2. API Access (Programmatic)

### List Documents
```bash
GET /api/v1/documents/list?limit=100
```

### Search Documents
```bash
GET /api/v1/documents/search?query=invoice
```

### Preview Document
```bash
GET /api/v1/documents/preview/{doc_id}
```

### View Document
```bash
GET /api/v1/documents/view/{doc_id}
```

### Download Document
```bash
GET /api/v1/documents/download/{doc_id}
```

### Upload Document
```bash
POST /api/v1/documents/upload
Content-Type: multipart/form-data
```

## 3. Integrated Chat Access

When using the LexOS chat interface, you can:
- Reference documents by name
- Ask questions about stored documents
- Request document summaries
- Search for specific content

Example prompts:
- "Show me all PDFs uploaded this week"
- "What's in the document about project requirements?"
- "Find all spreadsheets with budget data"

## 4. Mobile Access

The web interfaces are responsive and work on mobile devices:
- Touch-friendly interface
- Optimized for small screens
- Swipe between document list and viewer

## Security Features

- All access requires authentication (when enabled)
- Documents are stored securely in the vault
- Access is logged for audit trails
- Encrypted storage for sensitive files

## Remote Access Setup

To access from anywhere:

### 1. Local Network
```
http://192.168.x.x:8000/vault/
```

### 2. Port Forwarding
Configure your router to forward port 8000 to your LexOS server.

### 3. Reverse Proxy (Recommended)
Use nginx or Apache to proxy requests:

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. VPN Access
Connect to your network via VPN, then access normally.

### 5. Cloud Deployment
Deploy LexOS to a cloud provider for global access.

## Features by Access Method

| Feature | Web UI | API | Chat | Mobile |
|---------|--------|-----|------|---------|
| View Documents | ✅ | ✅ | ✅ | ✅ |
| Upload Files | ✅ | ✅ | ❌ | ✅ |
| Search | ✅ | ✅ | ✅ | ✅ |
| Preview | ✅ | ✅ | ❌ | ✅ |
| Download | ✅ | ✅ | ❌ | ✅ |
| OCR Text | Auto | Auto | ✅ | Auto |

## Quick Start

1. **Access the viewer**: Open `http://your-server:8000/vault/` in any browser
2. **Upload a document**: Drag and drop or click upload
3. **View documents**: Click any document to preview
4. **Search**: Use the search box to find specific files
5. **Download**: Click the download button for any file

## Integration with Memory System

All document access is tracked:
- Upload history is remembered
- Access patterns help with predictions
- Frequently accessed files are suggested
- Content is indexed for semantic search

The document vault is now fully integrated with LexOS's memory system, making your files accessible and searchable from anywhere!