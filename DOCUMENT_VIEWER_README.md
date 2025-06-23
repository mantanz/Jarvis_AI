# Document Viewer with Chunk Navigation

## Overview

The RAG system now includes a **standalone document viewer** that opens in a new tab, providing chunk-based navigation for PDF citations. This gives users more screen space and a dedicated environment for document exploration.

## How It Works

### 1. **Main RAG Interface (Port 8501)**
- Ask questions and get responses with citations
- Hover over citations (e.g., `[Source 1]`) to see tooltips with content previews
- View organized sources in expandable sections

### 2. **Standalone Document Viewer (Port 8503)**
- Opens in a new tab when you click navigation buttons
- Shows the PDF with a sidebar containing all citation sources
- Click on sources in the sidebar to navigate to specific chunks
- Includes page navigation, zoom controls, and chunk highlighting

## Getting Started

### 1. Start the Main RAG Application
```bash
streamlit run streamlit_app.py
```
This runs on `http://localhost:8501`

### 2. Start the Standalone Document Viewer
```bash
python3 run_standalone_viewer.py
```
This runs on `http://localhost:8503`

### 3. Use the System
1. Ask a question in the main interface
2. Get a response with citations
3. Expand the "📚 Sources" section
4. Click "🔍 Open Document Viewer" to view the entire document
5. Or click "📍 Go to Source" to jump directly to a specific citation

## Features

### Main Interface
- **Citation Tooltips**: Hover over `[Source X]` for content previews
- **Organized Sources**: Sources grouped by document with navigation buttons
- **Two Navigation Options**:
  - `🔍 Open Document Viewer`: View entire document with all citations
  - `📍 Go to Source`: Jump directly to a specific citation

### Document Viewer
- **Sidebar Navigation**: All citation sources listed with page numbers
- **Chunk Highlighting**: Click sources to see highlighted areas in the PDF
- **PDF Controls**: Page navigation, zoom in/out, page input
- **Active Source Tracking**: Currently selected source is highlighted
- **Smooth Navigation**: Animated transitions and highlighting effects

## Technical Details

### Architecture
- **Main App** (`streamlit_app.py`): Handles RAG queries and displays results
- **Standalone Viewer** (`standalone_pdf_viewer.py`): Dedicated PDF viewer with chunk navigation
- **URL Communication**: Chunk data passed via URL parameters between apps
- **Page Number Correction**: Automatic +1 offset for correct PDF navigation

### URL Structure
```
http://localhost:8503/?file=document.pdf&chunks=<encoded_chunk_data>&active=chunk-1
```

### Chunk Data Format
```json
[
  {
    "source_num": 1,
    "page": "12 (¶1.3)",
    "tooltip_text": "Content of the chunk..."
  }
]
```

## Benefits

1. **Better User Experience**: 
   - More screen space for document viewing
   - Dedicated navigation interface
   - No embedded viewer cluttering the chat

2. **Improved Navigation**:
   - Direct chunk-to-location mapping
   - Visual highlighting of cited content
   - Smooth page transitions

3. **Scalability**:
   - Separate processes for main app and viewer
   - Can handle multiple documents simultaneously
   - Easy to extend with additional viewer features

## Troubleshooting

### Common Issues

1. **Viewer doesn't open**: Make sure the standalone viewer is running on port 8503
2. **Wrong page navigation**: The system adds +1 to page numbers for correct PDF navigation
3. **Chunk data not loading**: Check that the URL parameters are properly encoded

### Running Both Services
You can run both services simultaneously:

**Terminal 1:**
```bash
streamlit run streamlit_app.py
```

**Terminal 2:**
```bash
python3 run_standalone_viewer.py
```

## Future Enhancements

- **Text Search**: Search within documents
- **Annotation Support**: Add notes to specific chunks
- **Multiple Document Comparison**: View multiple PDFs side by side
- **Export Features**: Save highlighted sections or annotations 