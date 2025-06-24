import streamlit as st
import streamlit.components.v1 as components
import base64
import json
from pathlib import Path
from typing import Dict, List, Any
import urllib.parse
import re

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
            st.markdown("🔙 **[Back to Chat](http://localhost:8502)**")
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
            
            # Use the page number as-is (already corrected in processing.py)
            page = chunk.get('page', 1)
            # Extract numeric part from page string (handles cases like '3 (¶1.2)')
            if isinstance(page, str):
                page_match = re.search(r'(\d+)', page)
                page_num = int(page_match.group(1)) if page_match else 1
            else:
                page_num = int(page) if isinstance(page, int) else 1
            
            chunk_map[chunk_id] = {
                'source_num': source_num,
                'page': page_num,
                'content': chunk.get('tooltip_text', '')[:200] + "...",
                'full_content': chunk.get('tooltip_text', ''),
                'search_text': chunk.get('tooltip_text', '')[:100]  # First 100 chars for search
            }
        
        # Generate the HTML for the standalone viewer
        viewer_html = self._generate_html(pdf_data, filename, chunk_map, active_chunk)
        
        # Display the component with full height (almost full screen)
        components.html(viewer_html, height=900, scrolling=False)
    
    def _generate_html(self, pdf_data: str, filename: str, chunk_map: Dict, active_chunk: str = "") -> str:
        """Generate HTML for the standalone PDF viewer."""
        chunk_map_json = json.dumps(chunk_map)
        
        # JavaScript code for text-layer based highlighting
        highlight_js = """
                function highlightChunk(chunkId) {
                    const chunk = chunkMap[chunkId];
                    
                    console.log('Highlighting chunk:', chunkId, chunk);
                    
                    if (!chunk) {
                        console.log('No chunk data found for:', chunkId);
                        return;
                    }
                    
                    // Clear previous highlights
                    const spans = document.querySelectorAll('.textLayer span');
                    spans.forEach(span => {
                        span.classList.remove('highlight');
                        span.style.background = '';
                        span.style.border = '';
                        span.style.borderRadius = '';
                    });
                    
                    // Get the full text content
                    let fullText = '';
                    if (chunk.full_content) {
                        fullText = chunk.full_content.trim();
                    } else if (chunk.search_text) {
                        fullText = chunk.search_text.trim();
                    } else if (chunk.content) {
                        fullText = chunk.content.trim();
                    }
                    
                    if (!fullText) {
                        console.log('No text content found for chunk:', chunk);
                        return;
                    }
                    
                    // Extract first 5 and last 5 words from the chunk
                    const words = fullText.split(/\\s+/).filter(word => word.length > 0);
                    if (words.length < 3) {
                        console.log('Text too short for reliable highlighting:', words.length, 'words');
                        showFallbackHighlight(chunk);
                        return;
                    }
                    
                    const firstWords = words.slice(0, Math.min(5, words.length)).join(' ').toLowerCase();
                    const lastWords = words.slice(-Math.min(5, words.length)).join(' ').toLowerCase();
                    
                    console.log('First 5 words:', firstWords);
                    console.log('Last 5 words:', lastWords);
                    
                    // Find spans containing the first and last words
                    let startSpan = null;
                    let endSpan = null;
                    let inHighlightRegion = false;
                    
                    // Build continuous text from spans to match against
                    let continuousText = '';
                    let spanTextMap = [];
                    
                    spans.forEach((span, index) => {
                        const spanText = span.textContent;
                        spanTextMap.push({
                            span: span,
                            text: spanText,
                            startIndex: continuousText.length,
                            endIndex: continuousText.length + spanText.length
                        });
                        continuousText += spanText + ' ';
                    });
                    
                    const continuousTextLower = continuousText.toLowerCase();
                    
                    // Find the positions of first and last word sequences
                    let startPos = continuousTextLower.indexOf(firstWords);
                    let endPos = continuousTextLower.lastIndexOf(lastWords);
                    
                    // If exact match fails, try partial matches
                    if (startPos === -1) {
                        // Try first 3 words, then 2, then 1
                        for (let i = Math.min(3, words.length); i >= 1; i--) {
                            const partialFirst = words.slice(0, i).join(' ').toLowerCase();
                            startPos = continuousTextLower.indexOf(partialFirst);
                            if (startPos !== -1) {
                                console.log('Found partial first match with', i, 'words:', partialFirst);
                                break;
                            }
                        }
                    }
                    
                    if (endPos === -1 || endPos <= startPos) {
                        // Try last 3 words, then 2, then 1
                        for (let i = Math.min(3, words.length); i >= 1; i--) {
                            const partialLast = words.slice(-i).join(' ').toLowerCase();
                            const tempPos = continuousTextLower.lastIndexOf(partialLast);
                            if (tempPos !== -1 && tempPos > startPos) {
                                endPos = tempPos + partialLast.length;
                                console.log('Found partial last match with', i, 'words:', partialLast);
                                break;
                            }
                        }
                    }
                    
                    if (startPos === -1 || endPos === -1 || endPos <= startPos) {
                        console.log('Could not find text boundaries, showing fallback');
                        showFallbackHighlight(chunk);
                        return;
                    }
                    
                    console.log('Text boundaries found:', startPos, 'to', endPos);
                    
                    // Highlight all spans that fall within the identified text region
                    let highlightedCount = 0;
                    let firstHighlight = null;
                    
                    spanTextMap.forEach(spanInfo => {
                        // Check if this span overlaps with our highlight region
                        if (spanInfo.endIndex > startPos && spanInfo.startIndex < endPos) {
                            spanInfo.span.classList.add('highlight');
                            spanInfo.span.style.background = 'rgba(255, 193, 7, 0.7)';
                            spanInfo.span.style.border = '2px solid #ff9800';
                            spanInfo.span.style.borderRadius = '6px';
                            spanInfo.span.style.boxShadow = '0 0 10px rgba(255, 152, 0, 0.5)';
                            spanInfo.span.style.display = 'inline-block';
                            spanInfo.span.style.padding = '2px 4px';
                            spanInfo.span.style.marginLeft = '-2px'; // or use translateX

                            
                            highlightedCount++;
                            
                            if (!firstHighlight) {
                                firstHighlight = spanInfo.span;
                            }
                            
                            console.log('Highlighted span:', spanInfo.text.substring(0, 50));
                        }
                    });
                    
                    console.log('Total highlights created:', highlightedCount);
                    
                    // Scroll to first highlight
                    if (firstHighlight) {
                        setTimeout(() => {
                            firstHighlight.scrollIntoView({ 
                                behavior: "smooth", 
                                block: "center",
                                inline: "center"
                            });
                        }, 500);
                    }
                    
                    // If no highlights were found, show a fallback message
                    if (highlightedCount === 0) {
                        console.log('No highlights created, showing fallback indicator');
                        showFallbackHighlight(chunk);
                    }
                }
                
                function showFallbackHighlight(chunk) {
                    // Create a temporary overlay message
                    const container = document.getElementById('pdf-container');
                    const fallback = document.createElement('div');
                    fallback.style.cssText = 
                        'position: absolute;' +
                        'top: 50%;' +
                        'left: 50%;' +
                        'transform: translate(-50%, -50%);' +
                        'background: rgba(255, 193, 7, 0.9);' +
                        'border: 3px solid #ff9800;' +
                        'border-radius: 12px;' +
                        'padding: 20px;' +
                        'z-index: 20;' +
                        'color: #e65100;' +
                        'font-weight: bold;' +
                        'font-size: 16px;' +
                        'text-align: center;' +
                        'box-shadow: 0 4px 20px rgba(0,0,0,0.3);' +
                        'max-width: 400px;';
                    
                    fallback.innerHTML = '📍 Source ' + chunk.source_num + ' content is on this page<br><span style="font-size: 12px; font-weight: normal;">Text highlighting not available for this content</span>';
                    
                    container.appendChild(fallback);
                    
                    setTimeout(() => {
                        if (fallback.parentNode) {
                            fallback.remove();
                        }
                    }, 4000);
                }"""
        
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
                .textLayer {{ position: absolute; left: 0; top: 0; right: 0; bottom: 0; overflow: hidden; opacity: 0.2; line-height: 1.0; }}
                .textLayer > span {{ color: transparent; position: absolute; white-space: pre; cursor: text; transform-origin: 0% 0%; }}
                .textLayer .highlight {{ background: rgba(255, 193, 7, 0.6) !important; border: 2px solid #ff9800 !important; border-radius: 4px !important; color: transparent !important; }}
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
                    <div id="pdf-container" style="display: none; position: relative;">
                        <canvas id="pdf-canvas"></canvas>
                        <div id="text-layer" class="textLayer"></div>
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
                        
                        chunkItem.innerHTML = 
                            '<div class="chunk-header">Source ' + chunk.source_num + '</div>' +
                            '<div class="chunk-page">Page ' + chunk.page + '</div>' +
                            '<div class="chunk-preview">' + chunk.content + '</div>';
                        
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
                
                {highlight_js}
                
                function renderPage(num) {{
                    pdfDoc.getPage(num).then(function(page) {{
                        const viewport = page.getViewport({{scale: scale}});
                        canvas.height = viewport.height;
                        canvas.width = viewport.width;
                        
                        // Render the PDF page on canvas
                        const renderContext = {{
                            canvasContext: ctx,
                            viewport: viewport
                        }};
                        
                        page.render(renderContext).promise.then(function() {{
                            // Clear existing text layer
                            const textLayer = document.getElementById('text-layer');
                            textLayer.innerHTML = '';
                            textLayer.style.left = canvas.offsetLeft + 'px';
                            textLayer.style.top = canvas.offsetTop + 'px';
                            textLayer.style.height = canvas.height + 'px';
                            textLayer.style.width = canvas.width + 'px';
                            
                            // Render text layer
                            page.getTextContent().then(function(textContent) {{
                                pdfjsLib.renderTextLayer({{
                                    textContent: textContent,
                                    container: textLayer,
                                    viewport: viewport,
                                    textDivs: []
                                }});
                            }});
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