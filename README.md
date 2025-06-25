# 🚀 Modern RAG Pipeline - React + FastAPI

A complete transformation of the RAG pipeline from Streamlit to a modern React frontend with FastAPI backend. This implementation provides a robust, scalable, and maintainable architecture for document processing and intelligent querying.

## 🏗️ **ARCHITECTURE OVERVIEW**

```
┌─────────────────────────────────────────────────────────────────┐
│                          Frontend (React)                      │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐           │
│  │ Chat         │ │ Document     │ │ PDF          │           │
│  │ Interface    │ │ Manager      │ │ Viewer       │           │
│  └──────────────┘ └──────────────┘ └──────────────┘           │
│                          │                                     │
│                    React Context                               │
│                      (State)                                   │
└─────────────────────────┼───────────────────────────────────────┘
                          │ HTTP/REST API
┌─────────────────────────┼───────────────────────────────────────┐
│                   Backend (FastAPI)                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐           │
│  │ Document     │ │ RAG          │ │ Citation     │           │
│  │ Processing   │ │ Pipeline     │ │ Management   │           │
│  └──────────────┘ └──────────────┘ └──────────────┘           │
└─────────────────────────┼───────────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────────┐
│                     Data Layer                                 │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐           │
│  │ ChromaDB     │ │ Vector       │ │ PDF          │           │
│  │ Database     │ │ Embeddings   │ │ Storage      │           │
│  └──────────────┘ └──────────────┘ └──────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

## ✨ **KEY FEATURES**

### 🎯 **Frontend (React)**
- **Modern UI/UX**: Beautiful, responsive interface with Tailwind CSS
- **Real-time Chat**: Interactive chat interface with typing indicators
- **Drag & Drop Upload**: Intuitive document upload with progress tracking
- **Smart Citations**: Interactive citations with hover tooltips and navigation
- **PDF Integration**: Embedded PDF viewer with chunk highlighting
- **State Management**: Centralized state with React Context
- **Error Handling**: Comprehensive error boundaries and user feedback

### ⚡ **Backend (FastAPI)**
- **RESTful API**: Clean, documented API endpoints
- **Async Processing**: Non-blocking document processing
- **Auto Documentation**: Interactive API docs at `/docs`
- **CORS Support**: Configured for frontend integration
- **File Management**: Efficient PDF storage and retrieval
- **Citation Enhancement**: Advanced citation processing and navigation

### 🧠 **RAG Pipeline**
- **Advanced Chunking**: Paragraph-aware document processing
- **Vector Search**: ChromaDB integration for semantic search
- **Citation Tracking**: Source attribution with page references
- **LLM Integration**: Ollama support for local inference
- **Smart Renumbering**: Dynamic citation reorganization

## 🚀 **QUICK START**

### **Option 1: Full Stack (Recommended)**
```bash
# Start both backend and frontend
./start_full_app.sh
```

### **Option 2: Individual Services**
```bash
# Terminal 1: Start Backend
./start_backend.sh

# Terminal 2: Start Frontend  
./start_frontend.sh
```

### **Access Points**
- 🌐 **Frontend App**: http://localhost:3000
- 📖 **Backend API**: http://localhost:8000
- 📚 **API Documentation**: http://localhost:8000/docs

## 📋 **PREREQUISITES**

### **System Requirements**
- **Python**: 3.8+ (for backend)
- **Node.js**: 16+ (for frontend)
- **npm**: 8+ (for package management)

### **External Services**
- **Ollama**: Local LLM inference
```bash
# Install Ollama from https://ollama.com/
ollama pull llama3.2:latest
ollama serve
```

## 📦 **INSTALLATION**

### **1. Backend Setup**
```bash
# Create virtual environment
python -m venv rag_env
source rag_env/bin/activate  # Windows: rag_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **2. Frontend Setup**
```bash
# Install Node.js dependencies
npm install
```

### **3. Environment Configuration**
Create environment variables:
```bash
# For React (can be set in scripts)
export REACT_APP_API_URL=http://localhost:8000
```

## 🏗️ **PROJECT STRUCTURE**

```
📁 Docs_RAG/
├── 🐍 Backend (Python/FastAPI)
│   ├── main.py                     # FastAPI application
│   ├── processing.py               # Document processing
│   ├── query_data.py              # RAG pipeline
│   ├── citation_manager.py        # Citation management
│   ├── document_service.py        # Document utilities
│   └── requirements.txt           # Python dependencies
│
├── ⚛️ Frontend (React)
│   ├── src/
│   │   ├── components/
│   │   │   ├── chat/              # Chat interface
│   │   │   │   ├── ChatInterface.js
│   │   │   │   ├── MessageBubble.js
│   │   │   │   └── CitationTooltip.js
│   │   │   ├── ui/                # Reusable UI components
│   │   │   │   ├── Button.js
│   │   │   │   ├── LoadingSpinner.js
│   │   │   │   └── DocumentUploader.js
│   │   │   └── MainInterface.js   # Main application layout
│   │   ├── contexts/
│   │   │   └── AppContext.js      # Global state management
│   │   ├── services/
│   │   │   └── api.js             # API communication
│   │   └── App.js                 # Root component
│   ├── public/
│   └── package.json               # Node.js dependencies
│
├── 🚀 Scripts
│   ├── start_backend.sh           # Backend startup
│   ├── start_frontend.sh          # Frontend startup
│   └── start_full_app.sh          # Full stack startup
│
└── 📊 Data
    ├── data/                      # PDF document storage
    └── chroma/                    # Vector database
```

## 🔧 **COMPONENT ARCHITECTURE**

### **React Components**

#### **Core Layout**
- `MainInterface`: Main application shell with sidebar and tabs
- `ChatInterface`: Real-time chat with RAG pipeline
- `DocumentUploader`: Drag & drop file upload with progress

#### **UI Components**
- `Button`: Configurable button with variants and loading states
- `LoadingSpinner`: Reusable loading indicators
- `MessageBubble`: Chat messages with citation integration

#### **Citation System**
- `CitationTooltip`: Interactive citation previews
- Smart parsing of `[Source X]` patterns
- Click-to-navigate functionality

### **API Endpoints**

#### **Document Management**
```http
POST   /documents/upload     # Upload and process PDFs
GET    /documents           # List all documents
GET    /documents/{id}/info # Get document details
DELETE /documents/clear     # Clear all documents
```

#### **RAG Operations**
```http
POST   /query               # Perform RAG query
GET    /citations/{id}/navigate # Get citation navigation
```

#### **Utilities**
```http
GET    /health              # Health check
GET    /documents/{id}/base64 # Get PDF as base64
```

## 🎨 **UI/UX FEATURES**

### **Modern Design**
- **Tailwind CSS**: Utility-first styling
- **Framer Motion**: Smooth animations and transitions
- **Responsive Layout**: Mobile-friendly design
- **Collapsible Sidebar**: Space-efficient navigation

### **User Experience**
- **Real-time Feedback**: Loading states and progress indicators
- **Toast Notifications**: Success/error messages
- **Keyboard Shortcuts**: Cmd/Ctrl+Enter to send messages
- **Auto-scroll**: Chat automatically scrolls to new messages

### **Accessibility**
- **Semantic HTML**: Proper ARIA labels and roles
- **Focus Management**: Keyboard navigation support
- **Screen Reader**: Compatible with assistive technologies

## 📚 **USAGE GUIDE**

### **1. Document Upload**
1. Navigate to the "Upload" tab
2. Drag & drop PDF files or click to browse
3. Monitor upload progress
4. Files are automatically processed and vectorized

### **2. Querying Documents**
1. Switch to "Chat" tab
2. Type your question in the input field
3. Press Enter or click Send
4. View results with interactive citations

### **3. Citation Navigation**
1. Click on `[Source X]` tags in responses
2. View citation details in tooltips
3. Navigate to specific document pages
4. Explore source content in PDF viewer

### **4. Document Management**
1. Use "Documents" tab to view uploaded files
2. Click "View" to open PDF viewer
3. Clear individual or all documents
4. Monitor document status and metadata

## 🔧 **CONFIGURATION**

### **Backend Configuration**
```python
# main.py - CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **Frontend Configuration**
```javascript
// src/services/api.js - API base URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

### **Processing Parameters**
```python
# processing.py - Chunking configuration
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,           # Adjust for your documents
    chunk_overlap=80,         # Maintain context overlap
    separators=["\n\n", "\n"] # Paragraph-aware splitting
)
```

## 🚀 **DEPLOYMENT**

### **Development**
```bash
# Full development stack
./start_full_app.sh
```

### **Production**
```bash
# Backend (production)
uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend (build)
npm run build
npx serve -s build -l 3000
```

## 🔍 **TROUBLESHOOTING**

### **Common Issues**

#### **Backend Connection**
```bash
# Check if FastAPI is running
curl http://localhost:8000/health

# Restart backend
./start_backend.sh
```

#### **Frontend Issues**
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Restart development server
npm start
```

#### **Ollama Problems**
```bash
# Ensure Ollama is running
ollama serve

# Pull/update model
ollama pull llama3.2:latest
```

### **Performance Optimization**

#### **Backend**
- Adjust chunk sizes for your document types
- Optimize embedding model selection
- Configure ChromaDB persistence settings

#### **Frontend**
- Enable React production build
- Implement code splitting for large components
- Optimize image and asset loading

## 🌟 **ADVANCED FEATURES**

### **Citation Enhancement**
- **Source Tracking**: Full document lineage
- **Page References**: Exact page and paragraph locations
- **Relevance Scoring**: ML-based relevance metrics
- **Content Previews**: Rich tooltip content

### **PDF Integration**
- **Text Layer Highlighting**: Precise text selection
- **Chunk Navigation**: Jump to specific content sections
- **Cross-platform Support**: Works on all modern browsers
- **Fallback Strategies**: Multiple highlighting approaches

### **State Management**
- **Centralized Store**: React Context with useReducer
- **Optimistic Updates**: Immediate UI feedback
- **Error Recovery**: Graceful error handling
- **Connection Monitoring**: Real-time backend status

## 🧪 **TESTING**

### **Backend Testing**
```bash
# Test API health
curl http://localhost:8000/health

# Test document upload
curl -X POST -F "files=@document.pdf" http://localhost:8000/documents/upload

# Test query
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "test question"}' \
  http://localhost:8000/query
```

### **Frontend Testing**
```bash
# Run React tests
npm test

# Manual testing
# 1. Upload documents via UI
# 2. Send queries in chat
# 3. Test citation navigation
```

## 📖 **API DOCUMENTATION**

Visit `http://localhost:8000/docs` for interactive API documentation with:
- **Request/Response Schemas**
- **Try It Out** functionality
- **Model Definitions**
- **Error Codes** reference

## 🤝 **CONTRIBUTING**

1. **Fork** the repository
2. **Create** a feature branch
3. **Implement** your changes
4. **Test** thoroughly
5. **Submit** a pull request

### **Development Guidelines**
- Follow React hooks patterns
- Use TypeScript for new components (future enhancement)
- Maintain FastAPI async patterns
- Add comprehensive error handling

## 📄 **LICENSE**

MIT License - see LICENSE file for details.

## 🙏 **ACKNOWLEDGMENTS**

- **React Team**: For the amazing frontend framework
- **FastAPI**: For the modern Python web framework
- **ChromaDB**: For vector database capabilities
- **Tailwind CSS**: For utility-first styling
- **Framer Motion**: For smooth animations
- **Ollama**: For local LLM integration
- **Langchain**: For document processing utilities

---

🚀 **Ready to explore intelligent document analysis with modern web technologies!**

## 🎯 **TRANSFORMATION SUMMARY**

This project successfully transforms a Streamlit-based RAG pipeline into a modern, scalable React + FastAPI architecture:

### **Before (Streamlit)**
- ❌ Server-side rendering
- ❌ Limited customization
- ❌ Monolithic architecture
- ❌ Basic UI components

### **After (React + FastAPI)**
- ✅ Client-side React application
- ✅ Fully customizable UI/UX
- ✅ Microservices architecture
- ✅ Modern component system
- ✅ Real-time interactions
- ✅ Professional deployment ready

The new architecture maintains all original RAG functionality while providing a superior user experience and development workflow. 