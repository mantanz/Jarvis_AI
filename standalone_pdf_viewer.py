import streamlit as st
import streamlit.components.v1 as components
import base64
import json
from pathlib import Path
from typing import Dict, List, Any
import urllib.parse

class StandalonePDFViewer:
    """
    Standalone PDF viewer that opens in a new tab with chunk navigation.
    This viewer receives chunk data via URL parameters and displays the PDF
    with navigation capabilities.
    """
    
    def __init__(self, data_path: str = "data"):
        self.data_path = Path(data_path)
    
    def create_viewer_page(self):
        """Create the standalone PDF viewer page."""
        st.set_page_config(
            page_title="Document Viewer",
            page_icon="📄",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
        
        # Hide Streamlit UI elements to make it look like a standalone app
        st.markdown("""
        <style>
        .stApp > header {visibility: hidden;}
        .stApp > .main > div:nth-child(1) {padding-top: 0rem;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display:none;}
        .stDecoration {display:none;}
        .stToolbar {display:none;}
        </style>
        """, unsafe_allow_html=True)
        
        # Get parameters from URL
        query_params = st.query_params
        filename = query_params.get("file", "")
        chunk_data = query_params.get("chunks", "")
        active_chunk = query_params.get("active", "")
        
        if not filename:
            st.error("❌ No document specified. This viewer should be opened from the main RAG interface.")
            st.info("🔙 [Return to Main Interface](http://localhost:8501)")
            st.stop()
        
        # Decode chunk data
        try:
            chunks = json.loads(urllib.parse.unquote(chunk_data)) if chunk_data else []
        except Exception as e:
            st.error(f"❌ Error loading document data: {e}")
            st.stop()
        
        # Minimal header
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            st.markdown("🔙 **[Back to Chat](http://localhost:8501)**")
        with col2:
            st.markdown(f"<h2 style='text-align: center; margin: 0;'>📄 {filename}</h2>", unsafe_allow_html=True)
        with col3:
            if chunks:
                st.markdown(f"<div style='text-align: right; color: #666;'>{len(chunks)} sources</div>", unsafe_allow_html=True)
        
        # Create the full-screen viewer
        self._create_standalone_viewer(filename, chunks, active_chunk)
    
    def _create_standalone_viewer(self, filename: str, chunks: List[Dict], active_chunk: str = ""):
        """Create the standalone PDF viewer with chunk navigation."""
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
        
        # Process chunks for viewer
        chunk_map = {}
        for chunk in chunks:
            source_num = chunk.get('source_num', 1)
            chunk_id = f"chunk-{source_num}"
            
            # Extract page number and add 1 for correct PDF navigation
            page = chunk.get('page', '1')
            import re
            page_match = re.search(r'(\d+)', str(page))
            page_num = int(page_match.group(1)) + 1 if page_match else 2
            
            chunk_map[chunk_id] = {
                'source_num': source_num,
                'page': page_num,
                'content': chunk.get('tooltip_text', '')[:200] + "...",
                'full_content': chunk.get('tooltip_text', '')
            }
        
        # Generate the HTML for the standalone viewer
        viewer_html = self._generate_html(pdf_data, filename, chunk_map, active_chunk)
        
        # Display the component with full height (almost full screen)
        components.html(viewer_html, height=900, scrolling=False)
    
    def _generate_html(self, pdf_data: str, filename: str, chunk_map: Dict, active_chunk: str = "") -> str:
        """Generate HTML for the standalone PDF viewer."""
        chunk_map_json = json.dumps(chunk_map)
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Document Viewer</title>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
            <style>
                body {{ margin: 0; font-family: Arial; display: flex; height: 100vh; }}
                .sidebar {{ width: 300px; background: white; border-right: 1px solid #ddd; padding: 15px; overflow-y: auto; }}
                .main-viewer {{ flex: 1; display: flex; flex-direction: column; }}
                .pdf-controls {{ background: #2196f3; color: white; padding: 10px; display: flex; gap: 10px; align-items: center; }}
                .pdf-canvas-container {{ flex: 1; padding: 20px; text-align: center; overflow: auto; background: #f9f9f9; position: relative; }}
                #pdf-canvas {{ border: 1px solid #ddd; background: white; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
                .chunk-item {{ background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px; padding: 12px; margin-bottom: 10px; cursor: pointer; transition: all 0.2s; }}
                .chunk-item:hover {{ background: #e3f2fd; border-color: #2196f3; }}
                .chunk-item.active {{ background: #fff3e0; border-color: #ff9800; }}
                .chunk-header {{ font-weight: bold; color: #1976d2; margin-bottom: 5px; }}
                .chunk-page {{ color: #666; font-size: 12px; margin-bottom: 8px; }}
                .chunk-preview {{ color: #333; font-size: 13px; line-height: 1.4; }}
                .highlight-overlay {{ position: absolute; background: rgba(255, 235, 59, 0.6); border: 2px solid #ffc107; border-radius: 4px; pointer-events: none; z-index: 10; animation: fadeHighlight 3s ease-in-out; }}
                @keyframes fadeHighlight {{ 0% {{ background: rgba(255, 235, 59, 0.8); }} 100% {{ background: rgba(255, 235, 59, 0.2); }} }}
                button {{ background: white; color: #2196f3; border: 1px solid white; padding: 8px 16px; border-radius: 4px; cursor: pointer; }}
                button:hover {{ background: rgba(255,255,255,0.9); }}
                button:disabled {{ background: rgba(255,255,255,0.5); color: #999; }}
                input[type="number"] {{ width: 60px; padding: 6px; border: 1px solid white; border-radius: 4px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="sidebar">
                <div style="font-weight: bold; margin-bottom: 15px; color: #333;">📚 Citation Sources</div>
                <div id="chunk-list"></div>
            </div>
            
            <div class="main-viewer">
                <div class="pdf-controls">
                    <button onclick="prevPage()">← Prev</button>
                    <button onclick="nextPage()">Next →</button>
                    <span>Page:</span>
                    <input type="number" id="page-input" min="1" value="1" onchange="goToPage()">
                    <span id="page-count">of ?</span>
                    <button onclick="zoomIn()">Zoom In</button>
                    <button onclick="zoomOut()">Zoom Out</button>
                    <span style="margin-left: auto; font-weight: bold;">{filename}</span>
                </div>
                
                <div class="pdf-canvas-container">
                    <div id="loading">Loading PDF...</div>
                    <div id="pdf-container" style="display: none;">
                        <canvas id="pdf-canvas"></canvas>
                    </div>
                </div>
            </div>
            
            <script>
                pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
                
                let pdfDoc = null;
                let pageNum = 1;
                let scale = 1.2;
                let canvas = document.getElementById('pdf-canvas');
                let ctx = canvas.getContext('2d');
                let chunkMap = {chunk_map_json};
                let activeChunk = '{active_chunk}';
                
                const pdfData = 'data:application/pdf;base64,{pdf_data}';
                
                pdfjsLib.getDocument(pdfData).promise.then(function(pdfDoc_) {{
                    pdfDoc = pdfDoc_;
                    document.getElementById('page-count').textContent = 'of ' + pdfDoc.numPages;
                    document.getElementById('page-input').max = pdfDoc.numPages;
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('pdf-container').style.display = 'block';
                    
                    renderPage(pageNum);
                    createChunkList();
                    
                    if (activeChunk) {{
                        setTimeout(() => navigateToChunk(activeChunk), 1000);
                    }}
                }});
                
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
                    
                    if (activeChunk) {{
                        document.getElementById('sidebar-' + activeChunk)?.classList.remove('active');
                    }}
                    activeChunk = chunkId;
                    document.getElementById('sidebar-' + chunkId)?.classList.add('active');
                    
                    if (chunk.page !== pageNum) {{
                        pageNum = chunk.page;
                        renderPage(pageNum);
                    }}
                    
                    setTimeout(() => highlightChunk(chunkId), 500);
                }}
                
                function highlightChunk(chunkId) {{
                    const chunk = chunkMap[chunkId];
                    const container = document.getElementById('pdf-container');
                    
                    container.querySelectorAll('.highlight-overlay').forEach(el => el.remove());
                    
                    const highlight = document.createElement('div');
                    highlight.className = 'highlight-overlay';
                    
                    const highlightHeight = 50;
                    const highlightWidth = canvas.width * 0.8;
                    const highlightTop = (chunk.source_num % 8) * 80 + 100;
                    const highlightLeft = canvas.width * 0.1;
                    
                    highlight.style.cssText = `
                        top: ${{highlightTop}}px;
                        left: ${{highlightLeft}}px;
                        width: ${{highlightWidth}}px;
                        height: ${{highlightHeight}}px;
                    `;
                    
                    container.appendChild(highlight);
                    setTimeout(() => highlight.remove(), 3000);
                }}
                
                function renderPage(num) {{
                    pdfDoc.getPage(num).then(function(page) {{
                        const viewport = page.getViewport({{scale: scale}});
                        canvas.height = viewport.height;
                        canvas.width = viewport.width;
                        
                        page.render({{
                            canvasContext: ctx,
                            viewport: viewport
                        }});
                    }});
                    
                    document.getElementById('page-input').value = num;
                }}
                
                function prevPage() {{ if (pageNum > 1) {{ pageNum--; renderPage(pageNum); }} }}
                function nextPage() {{ if (pageNum < pdfDoc.numPages) {{ pageNum++; renderPage(pageNum); }} }}
                function goToPage() {{
                    const inputPage = parseInt(document.getElementById('page-input').value);
                    if (inputPage >= 1 && inputPage <= pdfDoc.numPages) {{
                        pageNum = inputPage;
                        renderPage(pageNum);
                    }}
                }}
                function zoomIn() {{ scale += 0.2; renderPage(pageNum); }}
                function zoomOut() {{ if (scale > 0.4) {{ scale -= 0.2; renderPage(pageNum); }} }}
            </script>
        </body>
        </html>
        """

# Main function to run the standalone viewer
def main():
    viewer = StandalonePDFViewer()
    viewer.create_viewer_page()

if __name__ == "__main__":
    main() 