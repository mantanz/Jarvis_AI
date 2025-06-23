import os
import urllib.parse
from typing import Dict, Optional, Tuple
from pathlib import Path
import streamlit as st

class DocumentService:
    """
    Service for handling document navigation and serving functionality.
    Provides methods to generate navigation URLs and serve documents.
    """
    
    def __init__(self, data_path: str = "data"):
        self.data_path = Path(data_path)
        self.base_url = self._get_base_url()
    
    def _get_base_url(self) -> str:
        """Get the base URL for the application."""
        try:
            # Try to get Streamlit's base URL if available
            return st.get_option('server.baseUrlPath') or ""
        except:
            return ""
    
    def parse_chunk_id(self, chunk_id: str) -> Dict[str, str]:
        """
        Parse a chunk ID to extract document location information.
        Format: "data/filename.pdf:page:paragraph:chunk"
        """
        try:
            parts = chunk_id.split(":")
            if len(parts) >= 4:
                file_path, page, paragraph, chunk = parts[0], parts[1], parts[2], parts[3]
                filename = os.path.basename(file_path)
                return {
                    "file_path": file_path,
                    "filename": filename,
                    "page": page,
                    "paragraph": paragraph,
                    "chunk": chunk,
                    "full_path": str(self.data_path / filename)
                }
            else:
                # Fallback for simpler formats
                file_path = parts[0] if parts else "unknown"
                filename = os.path.basename(file_path)
                return {
                    "file_path": file_path,
                    "filename": filename,
                    "page": parts[1] if len(parts) > 1 else "1",
                    "paragraph": parts[2] if len(parts) > 2 else "1",
                    "chunk": parts[3] if len(parts) > 3 else "1",
                    "full_path": str(self.data_path / filename)
                }
        except Exception as e:
            st.error(f"Error parsing chunk ID {chunk_id}: {e}")
            return {
                "file_path": "unknown",
                "filename": "unknown",
                "page": "1",
                "paragraph": "1",
                "chunk": "1",
                "full_path": "unknown"
            }
    
    def generate_navigation_url(self, chunk_id: str, navigation_type: str = "web") -> str:
        """
        Generate a navigation URL for a specific chunk location.
        
        Args:
            chunk_id: The chunk identifier
            navigation_type: Type of navigation ("web", "system", "embedded")
        """
        location_info = self.parse_chunk_id(chunk_id)
        filename = location_info["filename"]
        page = location_info["page"]
        paragraph = location_info["paragraph"]
        
        if navigation_type == "web":
            # Generate URL for web-based PDF viewer
            params = {
                "file": filename,
                "page": page,
                "paragraph": paragraph,
                "action": "navigate"
            }
            query_string = urllib.parse.urlencode(params)
            return f"{self.base_url}/document-viewer?{query_string}"
        
        elif navigation_type == "system":
            # Generate file:// URL for system PDF viewer
            full_path = os.path.abspath(location_info["full_path"])
            # PDF anchor format: file:///path/to/file.pdf#page=N
            return f"file:///{full_path}#page={page}"
        
        elif navigation_type == "embedded":
            # Generate URL for embedded PDF component
            return f"#view-{filename}-page-{page}-para-{paragraph}"
        
        else:
            return "#"
    
    def get_document_info(self, chunk_id: str) -> Dict[str, any]:
        """
        Get comprehensive document information for a chunk.
        """
        location_info = self.parse_chunk_id(chunk_id)
        full_path = Path(location_info["full_path"])
        
        info = {
            **location_info,
            "exists": full_path.exists(),
            "size": full_path.stat().st_size if full_path.exists() else 0,
            "navigation_urls": {
                "web": self.generate_navigation_url(chunk_id, "web"),
                "system": self.generate_navigation_url(chunk_id, "system"),
                "embedded": self.generate_navigation_url(chunk_id, "embedded")
            }
        }
        
        return info
    
    def get_available_documents(self) -> list:
        """Get list of all available documents in the data directory."""
        documents = []
        if not self.data_path.exists():
            return documents
        
        for file_path in self.data_path.iterdir():
            if file_path.suffix.lower() == '.pdf':
                documents.append({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "size": file_path.stat().st_size,
                    "url": self.generate_system_url(file_path.name)
                })
        
        return documents
    
    def generate_system_url(self, filename: str) -> str:
        """Generate a system file URL for opening documents."""
        full_path = os.path.abspath(self.data_path / filename)
        return f"file:///{full_path}"
    
    def create_download_link(self, filename: str) -> str:
        """Create a download link for a document."""
        file_path = self.data_path / filename
        if file_path.exists():
            return str(file_path)
        return None 