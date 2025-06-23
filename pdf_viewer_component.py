import streamlit as st
import streamlit.components.v1 as components
import os
from pathlib import Path
import base64
from typing import Optional, Dict

class PDFViewerComponent:
    """
    Component for displaying PDFs with navigation capabilities in Streamlit.
    """
    
    def __init__(self, data_path: str = "data"):
        self.data_path = Path(data_path)
    
    def encode_pdf_to_base64(self, file_path: Path) -> Optional[str]:
        """Encode PDF file to base64 for embedding."""
        try:
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except Exception as e:
            st.error(f"Error encoding PDF: {e}")
            return None
    
    def create_pdf_viewer_html(self, pdf_base64: str, page: int = 1, filename: str = "document.pdf") -> str:
        """Create HTML for PDF.js viewer with navigation."""
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>PDF Viewer - {filename}</title>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
            <style>
                body {{
                    margin: 0;
                    padding: 20px;
                    font-family: Arial, sans-serif;
                    background-color: #f5f5f5;
                }}
                
                .pdf-controls {{
                    background: white;
                    padding: 10px;
                    border-radius: 5px;
                    margin-bottom: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    flex-wrap: wrap;
                }}
                
                .pdf-canvas-container {{
                    background: white;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    text-align: center;
                    min-height: 600px;
                }}
                
                #pdf-canvas {{
                    border: 1px solid #ddd;
                    max-width: 100%;
                    height: auto;
                }}
                
                .control-group {{
                    display: flex;
                    align-items: center;
                    gap: 5px;
                }}
                
                button {{
                    background: #0066cc;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 14px;
                }}
                
                button:hover {{
                    background: #0052a3;
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
            </style>
        </head>
        <body>
            <div class="pdf-controls">
                <div class="control-group">
                    <button id="prev-btn" onclick="prevPage()">← Previous</button>
                    <button id="next-btn" onclick="nextPage()">Next →</button>
                </div>
                
                <div class="control-group">
                    <span>Page:</span>
                    <input type="number" id="page-input" min="1" value="{page}" onchange="goToPage()">
                    <span id="page-count" class="info-text">of ?</span>
                </div>
                
                <div class="control-group">
                    <button onclick="zoomIn()">Zoom In</button>
                    <button onclick="zoomOut()">Zoom Out</button>
                    <button onclick="resetZoom()">Reset Zoom</button>
                </div>
                
                <div class="control-group">
                    <span class="info-text" id="filename">{filename}</span>
                </div>
            </div>
            
            <div class="pdf-canvas-container">
                <div id="loading" class="loading">Loading PDF...</div>
                <canvas id="pdf-canvas" style="display: none;"></canvas>
                <div id="error-message" class="error" style="display: none;"></div>
            </div>
            
            <script>
                // PDF.js setup
                pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
                
                let pdfDoc = null;
                let pageNum = {page};
                let pageRendering = false;
                let pageNumPending = null;
                let scale = 1.2;
                let canvas = document.getElementById('pdf-canvas');
                let ctx = canvas.getContext('2d');
                
                // Load PDF from base64
                const pdfData = 'data:application/pdf;base64,{pdf_base64}';
                
                // Load the PDF document
                pdfjsLib.getDocument(pdfData).promise.then(function(pdfDoc_) {{
                    pdfDoc = pdfDoc_;
                    document.getElementById('page-count').textContent = 'of ' + pdfDoc.numPages;
                    document.getElementById('page-input').max = pdfDoc.numPages;
                    document.getElementById('loading').style.display = 'none';
                    canvas.style.display = 'block';
                    
                    // Initial page render
                    renderPage(pageNum);
                }}).catch(function(error) {{
                    console.error('Error loading PDF:', error);
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('error-message').style.display = 'block';
                    document.getElementById('error-message').textContent = 'Error loading PDF: ' + error.message;
                }});
                
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
                    
                    // Update page counters
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
                
                // Initialize navigation buttons
                updateNavButtons();
            </script>
        </body>
        </html>
        """
        return html_template
    
    def display_pdf(self, filename: str, page: int = 1, height: int = 800) -> None:
        """Display a PDF with navigation in Streamlit."""
        file_path = self.data_path / filename
        
        if not file_path.exists():
            st.error(f"PDF file not found: {filename}")
            return
        
        # Encode PDF to base64
        pdf_base64 = self.encode_pdf_to_base64(file_path)
        if not pdf_base64:
            return
        
        # Create and display the PDF viewer
        html_content = self.create_pdf_viewer_html(pdf_base64, page, filename)
        components.html(html_content, height=height, scrolling=True)
    
    def create_simple_pdf_link(self, filename: str, page: int = 1) -> str:
        """Create a simple link to open PDF in system viewer."""
        file_path = self.data_path / filename
        if file_path.exists():
            abs_path = os.path.abspath(file_path)
            return f"file:///{abs_path}#page={page}"
        return "#"
    
    def display_pdf_download_button(self, filename: str, label: str = None, key: str = None) -> None:
        """Display a download button for the PDF."""
        file_path = self.data_path / filename
        
        if not file_path.exists():
            st.error(f"File not found: {filename}")
            return
        
        with open(file_path, "rb") as file:
            btn_label = label or f"📄 Download {filename}"
            # Create unique key if not provided
            unique_key = key or f"download_{filename}_{hash(str(file_path))}"
            st.download_button(
                label=btn_label,
                data=file,
                file_name=filename,
                mime="application/pdf",
                key=unique_key
            ) 