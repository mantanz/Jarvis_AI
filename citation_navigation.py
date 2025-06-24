from typing import List, Dict, Any
from citation_models import RenumberedCitation
from document_service import DocumentService
from pdf_viewer_component import PDFViewerComponent
import streamlit as st

class CitationNavigation:
    """
    Handles navigation functionality for citations.
    Extends the existing citation system without modifying it.
    """
    
    def __init__(self, data_path: str = "data"):
        self.document_service = DocumentService(data_path)
        self.pdf_viewer = PDFViewerComponent(data_path)
    
    def enhance_citations_with_navigation(self, citations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enhance citation dictionaries with navigation information.
        Adds navigation URLs and document info without modifying original structure.
        """
        enhanced_citations = []
        
        for citation in citations:
            # Create enhanced copy of citation
            enhanced_citation = citation.copy()
            
            # Extract chunk ID from metadata if available
            chunk_id = self._extract_chunk_id_from_citation(citation)
            
            if chunk_id:
                # Add navigation information
                doc_info = self.document_service.get_document_info(chunk_id)
                enhanced_citation.update({
                    "navigation_urls": doc_info["navigation_urls"],
                    "document_info": {
                        "filename": doc_info["filename"],
                        "page": doc_info["page"],
                        "paragraph": doc_info["paragraph"],
                        "chunk": doc_info["chunk"],
                        "exists": doc_info["exists"]
                    }
                })
            else:
                # Fallback navigation based on filename and page
                filename = citation.get("filename", "")
                page = self._extract_page_number(citation.get("page", "1"))
                
                enhanced_citation.update({
                    "navigation_urls": {
                        "system": self.document_service.generate_system_url(filename) + f"#page={page}",
                        "web": f"#view-{filename}-page-{page}",
                        "embedded": f"#embedded-{filename}-page-{page}"
                    },
                    "document_info": {
                        "filename": filename,
                        "page": str(page),
                        "paragraph": "1",
                        "chunk": "1",
                        "exists": self.document_service.data_path.joinpath(filename).exists()
                    }
                })
            
            enhanced_citations.append(enhanced_citation)
        
        return enhanced_citations
    
    def _extract_chunk_id_from_citation(self, citation: Dict[str, Any]) -> str:
        """Extract chunk ID from citation if available."""
        # Try to reconstruct chunk ID from citation data
        if "original_source_num" in citation and hasattr(citation, "source_id"):
            return citation.get("source_id", "")
        
        # Fallback: construct from available data
        filename = citation.get("filename", "")
        page = self._extract_page_number(citation.get("page", "1"))
        
        if filename:
            return f"data/{filename}:{page}:1:1"
        
        return ""
    
    def _extract_page_number(self, page_str: str) -> int:
        """Extract numeric page number from page string."""
        import re
        
        # Handle formats like "5 (¶2.1)" or just "5"
        match = re.search(r'(\d+)', str(page_str))
        if match:
            return int(match.group(1))
        return 1
    
    def _open_in_system(self, system_url: str) -> None:
        """Helper to open document in system viewer."""
        st.markdown(f'<a href="{system_url}" target="_blank">🔗 Click here to open the document</a>', 
                   unsafe_allow_html=True)
        
        # Try JavaScript approach
        st.components.v1.html(f"""
            <script>
                try {{
                    window.open('{system_url}', '_blank');
                }} catch(e) {{
                    console.error('Could not open document:', e);
                }}
            </script>
        """, height=0)
    
    def _show_embedded_pdf(self, filename: str, page: int = 1) -> None:
        """Show PDF in embedded viewer."""
        st.markdown(f"### 📖 Viewing: {filename} (Page {page})")
        self.pdf_viewer.display_pdf(filename, page, height=700)
    
    def _show_navigation_details(self, citation: Dict[str, Any]) -> None:
        """Show detailed navigation information."""
        doc_info = citation.get("document_info", {})
        nav_urls = citation.get("navigation_urls", {})
        
        st.markdown("### 📍 Document Location Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Document Info:**")
            st.write(f"📄 **File:** {doc_info.get('filename', 'Unknown')}")
            st.write(f"📖 **Page:** {doc_info.get('page', 'Unknown')}")
            st.write(f"📝 **Paragraph:** {doc_info.get('paragraph', 'Unknown')}")
            st.write(f"📋 **Chunk:** {doc_info.get('chunk', 'Unknown')}")
        
        with col2:
            st.markdown("**Navigation Options:**")
            if nav_urls.get("system"):
                st.markdown(f"🔗 [Open in System Viewer]({nav_urls['system']})")
            
            unique_key = citation.get('unique_key', f"src_{citation['source_num']}")
            if st.button("📖 View in Embedded Viewer", key=f"detailed_view_{unique_key}"):
                page_num = int(self._extract_page_number(doc_info.get('page', '1')))
                self._show_embedded_pdf(doc_info.get('filename', ''), page_num)
    
    def create_citation_with_navigation_tooltip(self, citation: Dict[str, Any]) -> str:
        """
        Create a citation tooltip that includes navigation options.
        Extends the existing tooltip functionality.
        """
        base_tooltip = citation.get("tooltip_text", "")
        doc_info = citation.get("document_info", {})
        nav_urls = citation.get("navigation_urls", {})
        
        if not doc_info.get("exists", False):
            navigation_section = "\n\n🚫 Document not available"
        else:
            filename = doc_info.get("filename", "Unknown")
            page = doc_info.get("page", "1")
            
            navigation_section = f"""

            📍 Location: {filename}, Page {page}
            🔗 Right-click citation to open document
            📖 Use document viewer for detailed view
            """
        
        return base_tooltip + navigation_section
