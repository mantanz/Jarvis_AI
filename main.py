from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil
import json
import base64
from pathlib import Path
import tempfile

# Import existing modules
from processing import load_documents, split_documents, add_to_chroma, clear_database
from query_data import query_rag
from document_service import DocumentService
from citation_manager import CitationManager
# from citation_navigation import CitationNavigation

app = FastAPI(title="RAG Pipeline API", description="API for document processing and RAG queries")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8501", "http://localhost:8502"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
document_service = DocumentService()
# citation_manager = CitationManager()  # Will be created per request
# citation_nav = CitationNavigation()

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    include_html: bool = True

class QueryResponse(BaseModel):
    response_text: str
    citations: List[dict]
    enhanced_citations: List[dict]
    formatted_response: str
    html_response_with_tooltips: str
    total_citations_used: int

class DocumentInfo(BaseModel):
    filename: str
    size: int
    path: str
    url: str

class ProcessingStatus(BaseModel):
    status: str
    message: str
    documents_processed: int = 0

# Mount static files for serving PDFs
app.mount("/static", StaticFiles(directory="data"), name="static")

@app.get("/")
async def root():
    return {"message": "RAG Pipeline API is running"}

@app.post("/documents/upload", response_model=ProcessingStatus)
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload and process documents for RAG pipeline."""
    try:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        uploaded_files = []
        
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF")
            
            # Save uploaded file
            file_path = Path("data") / file.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            uploaded_files.append(file.filename)
        
        # Process documents
        documents = load_documents()
        chunks = split_documents(documents)
        add_to_chroma(chunks)
        
        return ProcessingStatus(
            status="success",
            message=f"Successfully processed {len(uploaded_files)} documents",
            documents_processed=len(uploaded_files)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing documents: {str(e)}")

@app.get("/documents", response_model=List[DocumentInfo])
async def list_documents():
    """Get list of all available documents."""
    try:
        documents = document_service.get_available_documents()
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving documents: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query documents using RAG pipeline."""
    try:
        result = query_rag(request.query)
        
        # Enhance citations with navigation data
        enhanced_citations = result["citations"]  # For now, just use basic citations
        
        return QueryResponse(
            response_text=result["response_text"],
            citations=result["citations"],
            enhanced_citations=enhanced_citations,
            formatted_response=result["formatted_response"],
            html_response_with_tooltips=result["html_response_with_tooltips"],
            total_citations_used=result["total_citations_used"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying documents: {str(e)}")

@app.get("/documents/{filename}/info")
async def get_document_info(filename: str):
    """Get detailed information about a specific document."""
    try:
        # Create a mock chunk ID for the document
        chunk_id = f"data/{filename}:1:1:1"
        info = document_service.get_document_info(chunk_id)
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting document info: {str(e)}")

@app.get("/documents/{filename}/download")
async def download_document(filename: str):
    """Download a specific document."""
    try:
        file_path = Path("data") / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Document not found")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/pdf'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading document: {str(e)}")

@app.get("/documents/{filename}/base64")
async def get_document_base64(filename: str):
    """Get document as base64 encoded string for PDF viewer."""
    try:
        file_path = Path("data") / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Document not found")
        
        with open(file_path, "rb") as f:
            pdf_data = base64.b64encode(f.read()).decode()
        
        return {"filename": filename, "data": pdf_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error encoding document: {str(e)}")

@app.post("/documents/clear", response_model=ProcessingStatus)
async def clear_documents():
    """Clear all documents and reset the database."""
    try:
        # Clear the vector database
        clear_database()
        
        # Remove all PDF files from data directory (optional)
        data_path = Path("data")
        if data_path.exists():
            for file_path in data_path.glob("*.pdf"):
                file_path.unlink()
        
        return ProcessingStatus(
            status="success",
            message="Successfully cleared all documents and database"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing documents: {str(e)}")

@app.get("/citations/{source_num}/navigate")
async def get_citation_navigation(source_num: int, nav_type: str = "web"):
    """Get navigation URL for a specific citation."""
    try:
        # This would need to be enhanced based on your citation data
        # For now, return a basic navigation structure
        return {
            "source_num": source_num,
            "navigation_type": nav_type,
            "url": f"/pdf-viewer?source={source_num}&type={nav_type}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting citation navigation: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "RAG Pipeline API is operational"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 