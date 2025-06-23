import streamlit as st
import streamlit.components.v1 as components
import base64
import json
from pathlib import Path
from typing import Dict, List, Any

class ChunkPDFViewer:
    """
    PDF viewer component with chunk-based navigation and highlighting.
    Maps citation chunks to specific locations in the PDF for precise navigation.
    """
    
    def __init__(self, data_path: str = "data"):
        self.data_path = Path(data_path)
    
    def create_chunk_mapped_viewer(self, filename: str, citations: List[Dict[str, Any]], height: int = 700) -> None:
        """
        Create a PDF viewer with chunk mapping and citation highlighting.
        
        Args:
            filename: PDF filename to display
            citations: List of citations with chunk information
            height: Height of the viewer component
        """
        file_path = self.data_path / filename
        
        if not file_path.exists():
            st.error(f"PDF file not found: {filename}")
            return
        
        # Encode PDF to base64
        try:
            with open(file_path, "rb") as f:
                pdf_data = base64.b64encode(f.read()).decode()
        except Exception as e:
            st.error(f"Error loading PDF: {e}")
            return
        
        # Create chunk mapping from citations
        chunk_map = self._create_chunk_mapping(citations)
        
        # Generate the HTML with embedded PDF and chunk navigation
        viewer_html = self._generate_viewer_html(pdf_data, filename, chunk_map)
        
        # Display the component
        components.html(viewer_html, height=height, scrolling=True)
    
    def _create_chunk_mapping(self, citations: List[Dict[str, Any]]) -> Dict[str, Dict]:
        """Create a mapping of chunk IDs to their metadata."""
        chunk_map = {}
        
        for citation in citations:
            # Extract chunk information
            source_num = citation.get('source_num')
            filename = citation.get('filename', '')
            page = citation.get('page', '1')
            content = citation.get('tooltip_text', '')
            
            # Extract page number and add 1 for correct PDF navigation
            # The page numbers in citations are 1-based, but PDF viewer needs +1 offset
            import re
            page_match = re.search(r'(\d+)', str(page))
            page_num = int(page_match.group(1)) + 1 if page_match else 2
            
            # Create chunk ID
            chunk_id = f"chunk-{source_num}"
            
            chunk_map[chunk_id] = {
                'source_num': source_num,
                'page': page_num,
                'content': content[:200] + "..." if len(content) > 200 else content,
                'full_content': content
            }
        
        return chunk_map
    
    def _generate_viewer_html(self, pdf_data: str, filename: str, chunk_map: Dict) -> str:
        """Generate the complete HTML for the PDF viewer with chunk navigation."""
        
        # Convert chunk_map to JSON for JavaScript
        chunk_map_json = json.dumps(chunk_map)
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Chunk PDF Viewer - {filename}</title>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    font-family: Arial, sans-serif;
                    background-color: #f5f5f5;
                    display: flex;
                    height: 100vh;
                }}
                
                .sidebar {{
                    width: 300px;
                    background: white;
                    border-right: 1px solid #ddd;
                    overflow-y: auto;
                    padding: 15px;
                    box-shadow: 2px 0 4px rgba(0,0,0,0.1);
                }}
                
                .main-viewer {{
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    background: white;
                }}
                
                .pdf-controls {{
                    background: white;
                    padding: 10px 15px;
                    border-bottom: 1px solid #ddd;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    flex-wrap: wrap;
                }}
                
                .pdf-canvas-container {{
                    flex: 1;
                    padding: 20px;
                    text-align: center;
                    overflow: auto;
                    background: #f9f9f9;
                }}
                
                #pdf-canvas {{
                    border: 1px solid #ddd;
                    max-width: 100%;
                    height: auto;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    background: white;
                }}
                
                .chunk-item {{
                    background: #f8f9fa;
                    border: 1px solid #e9ecef;
                    border-radius: 6px;
                    padding: 12px;
                    margin-bottom: 10px;
                    cursor: pointer;
                    transition: all 0.2s ease;
                }}
                
                .chunk-item:hover {{
                    background: #e3f2fd;
                    border-color: #2196f3;
                    transform: translateY(-1px);
                }}
                
                .chunk-item.active {{
                    background: #fff3e0;
                    border-color: #ff9800;
                    box-shadow: 0 2px 4px rgba(255,152,0,0.2);
                }}
                
                .chunk-header {{
                    font-weight: bold;
                    color: #1976d2;
                    margin-bottom: 5px;
                    font-size: 14px;
                }}
                
                .chunk-page {{
                    color: #666;
                    font-size: 12px;
                    margin-bottom: 8px;
                }}
                
                .chunk-preview {{
                    color: #333;
                    font-size: 13px;
                    line-height: 1.4;
                    overflow: hidden;
                    display: -webkit-box;
                    -webkit-line-clamp: 3;
                    -webkit-box-orient: vertical;
                }}
                
                .highlight-overlay {{
                    position: absolute;
                    background: rgba(255, 235, 59, 0.4);
                    border: 2px solid #ffc107;
                    border-radius: 4px;
                    pointer-events: none;
                    transition: all 0.3s ease;
                    z-index: 10;
                }}
                
                .fade-highlight {{
                    animation: fadeHighlight 3s ease-in-out;
                }}
                
                @keyframes fadeHighlight {{
                    0% {{ background: rgba(255, 235, 59, 0.8); }}
                    50% {{ background: rgba(255, 235, 59, 0.6); }}
                    100% {{ background: rgba(255, 235, 59, 0.2); }}
                }}
                
                button {{
                    background: #1976d2;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 14px;
                    transition: background 0.2s;
                }}
                
                button:hover {{
                    background: #1565c0;
                }}
                
                button:disabled {{
                    background: #ccc;
                    cursor: not-allowed;
                }}
                
                input[type="number"] {{
                    width: 60px;
                    padding: 6px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    text-align: center;
                }}
                
                .info-text {{
                    color: #666;
                    font-size: 14px;
                }}
                
                .loading {{
                    color: #666;
                    font-size: 16px;
                    padding: 40px;
                }}
                
                .error {{
                    color: #d32f2f;
                    background: #ffebee;
                    padding: 15px;
                    border-radius: 4px;
                    border-left: 4px solid #d32f2f;
                }}
                
                .sidebar-header {{
                    font-size: 16px;
                    font-weight: bold;
                    margin-bottom: 15px;
                    color: #333;
                    border-bottom: 2px solid #e0e0e0;
                    padding-bottom: 8px;
                }}
            </style>
        </head>
        <body>
            <div class="sidebar">
                <div class="sidebar-header">📚 Citation Sources</div>
                <div id="chunk-list"></div>
            </div>
            
            <div class="main-viewer">
                <div class="pdf-controls">
                    <button id="prev-btn" onclick="prevPage()">← Previous</button>
                    <button id="next-btn" onclick="nextPage()">Next →</button>
                    
                    <span>Page:</span>
                    <input type="number" id="page-input" min="1" value="1" onchange="goToPage()">
                    <span id="page-count" class="info-text">of ?</span>
                    
                    <button onclick="zoomIn()">Zoom In</button>
                    <button onclick="zoomOut()">Zoom Out</button>
                    <button onclick="resetZoom()">Reset Zoom</button>
                    
                    <span class="info-text" id="filename">{filename}</span>
                </div>
                
                <div class="pdf-canvas-container">
                    <div id="loading" class="loading">Loading PDF...</div>
                    <div id="pdf-container" style="position: relative; display: none;">
                        <canvas id="pdf-canvas"></canvas>
                    </div>
                    <div id="error-message" class="error" style="display: none;"></div>
                </div>
            </div>
            
            <script>
                // PDF.js setup
                pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
                
                let pdfDoc = null;
                let pageNum = 1;
                let pageRendering = false;
                let pageNumPending = null;
                let scale = 1.2;
                let canvas = document.getElementById('pdf-canvas');
                let ctx = canvas.getContext('2d');
                let chunkMap = {chunk_map_json};
                let activeChunk = null;
                
                // Load PDF from base64
                const pdfData = 'data:application/pdf;base64,{pdf_data}';
                
                // Initialize the viewer
                initializeViewer();
                
                function initializeViewer() {{
                    // Load PDF
                    pdfjsLib.getDocument(pdfData).promise.then(function(pdfDoc_) {{
                        pdfDoc = pdfDoc_;
                        document.getElementById('page-count').textContent = 'of ' + pdfDoc.numPages;
                        document.getElementById('page-input').max = pdfDoc.numPages;
                        document.getElementById('loading').style.display = 'none';
                        document.getElementById('pdf-container').style.display = 'block';
                        
                        renderPage(pageNum);
                        createChunkList();
                    }}).catch(function(error) {{
                        console.error('Error loading PDF:', error);
                        document.getElementById('loading').style.display = 'none';
                        document.getElementById('error-message').style.display = 'block';
                        document.getElementById('error-message').textContent = 'Error loading PDF: ' + error.message;
                    }});
                }}
                
                function createChunkList() {{
                    const chunkList = document.getElementById('chunk-list');
                    
                    Object.keys(chunkMap).forEach(chunkId => {{
                        const chunk = chunkMap[chunkId];
                        const chunkItem = document.createElement('div');
                        chunkItem.className = 'chunk-item';
                        chunkItem.id = 'sidebar-' + chunkId;
                        chunkItem.onclick = () => navigateToChunk(chunkId);
                        
                        chunkItem.innerHTML = `
                            <div class="chunk-header">Source ${{chunk.source_num}}</div>
                            <div class="chunk-page">Page ${{chunk.page}}</div>
                            <div class="chunk-preview">${{chunk.content}}</div>
                        `;
                        
                        chunkList.appendChild(chunkItem);
                    }});
                }}
                
                function navigateToChunk(chunkId) {{
                    const chunk = chunkMap[chunkId];
                    if (!chunk) return;
                    
                    // Update active chunk
                    if (activeChunk) {{
                        document.getElementById('sidebar-' + activeChunk)?.classList.remove('active');
                    }}
                    activeChunk = chunkId;
                    document.getElementById('sidebar-' + chunkId)?.classList.add('active');
                    
                    // Navigate to page
                    if (chunk.page !== pageNum) {{
                        pageNum = chunk.page;
                        renderPage(pageNum);
                    }}
                    
                    // Highlight the chunk area (simulated)
                    setTimeout(() => {{
                        highlightChunkOnPage(chunkId);
                    }}, 500);
                }}
                
                function highlightChunkOnPage(chunkId) {{
                    const chunk = chunkMap[chunkId];
                    
                    // Create highlight overlay (simplified - you could make this more sophisticated)
                    const canvasRect = canvas.getBoundingClientRect();
                    const container = document.getElementById('pdf-container');
                    
                    // Remove existing highlights
                    container.querySelectorAll('.highlight-overlay').forEach(el => el.remove());
                    
                    // Create new highlight (example position - you could improve this)
                    const highlight = document.createElement('div');
                    highlight.className = 'highlight-overlay fade-highlight';
                    
                    // Position highlight based on chunk content (simplified)
                    const highlightHeight = 40;
                    const highlightWidth = canvas.width * 0.8;
                    const highlightTop = (chunk.source_num % 10) * 60 + 100; // Simplified positioning
                    const highlightLeft = canvas.width * 0.1;
                    
                    highlight.style.cssText = `
                        top: ${{highlightTop}}px;
                        left: ${{highlightLeft}}px;
                        width: ${{highlightWidth}}px;
                        height: ${{highlightHeight}}px;
                    `;
                    
                    container.appendChild(highlight);
                    
                    // Remove highlight after animation
                    setTimeout(() => {{
                        highlight.remove();
                    }}, 3000);
                }}
                
                function renderPage(num) {{
                    pageRendering = true;
                    
                    pdfDoc.getPage(num).then(function(page) {{
                        const viewport = page.getViewport({{scale: scale}});
                        canvas.height = viewport.height;
                        canvas.width = viewport.width;
                        
                        const renderContext = {{
                            canvasContext: ctx,
                            viewport: viewport
                        }};
                        
                        const renderTask = page.render(renderContext);
                        
                        renderTask.promise.then(function() {{
                            pageRendering = false;
                            if (pageNumPending !== null) {{
                                renderPage(pageNumPending);
                                pageNumPending = null;
                            }}
                        }});
                    }});
                    
                    document.getElementById('page-input').value = num;
                    updateNavButtons();
                }}
                
                function queueRenderPage(num) {{
                    if (pageRendering) {{
                        pageNumPending = num;
                    }} else {{
                        renderPage(num);
                    }}
                }}
                
                function prevPage() {{
                    if (pageNum <= 1) return;
                    pageNum--;
                    queueRenderPage(pageNum);
                }}
                
                function nextPage() {{
                    if (pageNum >= pdfDoc.numPages) return;
                    pageNum++;
                    queueRenderPage(pageNum);
                }}
                
                function goToPage() {{
                    const inputPage = parseInt(document.getElementById('page-input').value);
                    if (inputPage >= 1 && inputPage <= pdfDoc.numPages) {{
                        pageNum = inputPage;
                        queueRenderPage(pageNum);
                    }}
                }}
                
                function updateNavButtons() {{
                    document.getElementById('prev-btn').disabled = (pageNum <= 1);
                    document.getElementById('next-btn').disabled = (pageNum >= pdfDoc.numPages);
                }}
                
                function zoomIn() {{
                    scale += 0.2;
                    queueRenderPage(pageNum);
                }}
                
                function zoomOut() {{
                    if (scale > 0.4) {{
                        scale -= 0.2;
                        queueRenderPage(pageNum);
                    }}
                }}
                
                function resetZoom() {{
                    scale = 1.2;
                    queueRenderPage(pageNum);
                }}
                
                // Listen for external chunk navigation
                window.addEventListener('message', function(event) {{
                    if (event.data && event.data.type === 'navigateToChunk') {{
                        navigateToChunk(event.data.chunkId);
                    }}
                }});
                
                // Initialize navigation buttons
                updateNavButtons();
            </script>
        </body>
        </html>
        """
        
        return html_template
    
    def create_citation_link(self, source_num: int, viewer_id: str = "pdf-viewer") -> str:
        """
        Create a citation link that navigates to a specific chunk in the PDF viewer.
        
        Args:
            source_num: Source number to link to
            viewer_id: ID of the PDF viewer component
        
        Returns:
            HTML string for the clickable citation
        """
        chunk_id = f"chunk-{source_num}"
        
        citation_html = f'''
        <span class="citation-link" 
              onclick="
                const iframe = document.querySelector('iframe[title*=\"Chunk PDF Viewer\"]');
                if (iframe && iframe.contentWindow) {{
                    iframe.contentWindow.postMessage({{
                        type: 'navigateToChunk',
                        chunkId: '{chunk_id}'
                    }}, '*');
                }}
              "
              style="cursor: pointer; color: #1976d2; text-decoration: underline; font-weight: bold;">
            [Source {source_num}]
        </span>
        '''
        
        return citation_html 