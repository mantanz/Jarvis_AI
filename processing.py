
import argparse
import os
import shutil
from langchain_community.document_loaders.pdf import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from get_embedding_function import get_embedding_function
from langchain_community.vectorstores import Chroma


CHROMA_PATH = "chroma"
DATA_PATH = "data"


def main():

    # Check if the database should be cleared (using the --clear flag).
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()
    if args.reset:
        print("Clearing Database")
        clear_database()

    # Create (or update) the data store.
    documents = load_documents()
    chunks = split_documents(documents)
    add_to_chroma(chunks)


def load_documents():
    document_loader = PyPDFDirectoryLoader(DATA_PATH)
    return document_loader.load()


def split_documents(documents: list[Document]):
    """
    Custom paragraph-aware chunking that respects paragraph boundaries.
    Chunks are filled to maximum capacity but never cross paragraph boundaries.
    """
    chunk_size = 800
    chunks = []
    
    for doc in documents:
        # Split document into paragraphs using improved detection
        paragraphs = detect_paragraphs(doc.page_content)
        
        # Process each paragraph with strict boundary respect
        for para_idx, paragraph in enumerate(paragraphs, 1):
            paragraph_chunks = split_paragraph_into_chunks(
                paragraph, 
                chunk_size, 
                doc.metadata, 
                para_idx
            )
            chunks.extend(paragraph_chunks)
    
    return chunks


def detect_paragraphs(text: str):
    """
    Detect paragraph boundaries in PDF-extracted text using conservative heuristics.
    Focus on clear paragraph breaks rather than sentence breaks.
    """
    import re
    
    # Normalize the text first
    text = text.strip()
    
    # Replace various paragraph separators with a consistent marker
    # Pattern 1: Double newlines with optional whitespace (standard paragraph break)
    text = re.sub(r'\n\s*\n+', '§PARA§', text)
    
    # Pattern 2: Sentence ending followed by newline and clear paragraph starters
    paragraph_starters = [
        r'([.!?])\s*\n\s*(An example of)',
        r'([.!?])\s*\n\s*(For instance)',
        r'([.!?])\s*\n\s*(However)',
        r'([.!?])\s*\n\s*(Moreover)',
        r'([.!?])\s*\n\s*(Furthermore)',
        r'([.!?])\s*\n\s*(In addition)',
        r'([.!?])\s*\n\s*(Therefore)',
        r'([.!?])\s*\n\s*(Thus)',
        r'([.!?])\s*\n\s*(Consequently)',
        r'([.!?])\s*\n\s*(In conclusion)',
        r'([.!?])\s*\n\s*([A-Z][A-Z\s]+ [A-Z])',  # ALL CAPS titles/headers
        r'([.!?])\s*\n\s*([0-9]+\.)',  # Numbered sections
    ]
    
    for pattern in paragraph_starters:
        text = re.sub(pattern, r'\1§PARA§\2', text, flags=re.IGNORECASE)
    
    # Pattern 3: Sentence ending followed by newline and what looks like a new topic
    # Be very conservative - only split if it's clearly a new paragraph
    text = re.sub(r'([.!?])\s*\n\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+[A-Z])', r'\1§PARA§\2', text)
    
    # Pattern 4: Handle specific cases like titles or headers
    text = re.sub(r'([.!?])\s*\n\s*([A-Z][-\w\s]+ Event)', r'\1§PARA§\2', text)
    text = re.sub(r'([.!?])\s*\n\s*(Imagine)', r'\1§PARA§\2', text)
    
    # Pattern 5: Split titles/headers from their following content
    text = re.sub(r'([A-Z][-\w\s]+ Event)\s*\n\s*([A-Z][a-z])', r'\1§PARA§\2', text)
    
    # Split on our marker and clean up
    paragraphs = []
    for para in text.split('§PARA§'):
        # Clean up the paragraph
        para = re.sub(r'\n+', ' ', para)  # Replace internal newlines with spaces
        para = re.sub(r'\s+', ' ', para)  # Normalize whitespace
        para = para.strip()
        
        if para and len(para) > 20:  # Only keep substantial paragraphs
            paragraphs.append(para)
    
    return paragraphs


def split_paragraph_into_chunks(paragraph: str, chunk_size: int, base_metadata: dict, para_idx: int):
    """
    Split a single paragraph into chunks without crossing paragraph boundaries.
    Each chunk is filled to maximum capacity within the paragraph.
    """
    chunks = []
    
    # If paragraph fits in one chunk, return it as is
    if len(paragraph) <= chunk_size:
        chunk = Document(
            page_content=paragraph,
            metadata={
                **base_metadata,
                "paragraph_num": para_idx,
                "chunk_in_paragraph": 1
            }
        )
        chunks.append(chunk)
        return chunks
    
    # Split paragraph into sentences for better chunking
    sentences = split_into_sentences(paragraph)
    
    current_chunk = ""
    chunk_in_para = 1
    
    for sentence in sentences:
        # Check if adding this sentence would exceed chunk size
        potential_chunk = current_chunk + (" " if current_chunk else "") + sentence
        
        if len(potential_chunk) <= chunk_size:
            # Add sentence to current chunk
            current_chunk = potential_chunk
        else:
            # Current chunk is full, save it and start a new one
            if current_chunk:
                chunk = Document(
                    page_content=current_chunk.strip(),
                    metadata={
                        **base_metadata,
                        "paragraph_num": para_idx,
                        "chunk_in_paragraph": chunk_in_para
                    }
                )
                chunks.append(chunk)
                chunk_in_para += 1
            
            # Start new chunk with current sentence
            current_chunk = sentence
    
    # Add the last chunk if it has content
    if current_chunk:
        chunk = Document(
            page_content=current_chunk.strip(),
            metadata={
                **base_metadata,
                "paragraph_num": para_idx,
                "chunk_in_paragraph": chunk_in_para
            }
        )
        chunks.append(chunk)
    
    return chunks


def split_into_sentences(text: str):
    """
    Split text into sentences using simple heuristics.
    This is a basic implementation - could be enhanced with more sophisticated NLP.
    """
    import re
    
    # Split on sentence endings, but be careful with abbreviations
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    
    # If no sentence splits found, split on other punctuation or length
    if len(sentences) == 1 and len(text) > 400:
        # Fallback: split on commas, semicolons, or at word boundaries
        parts = re.split(r'[,;]\s+|(?<=\w)\s+(?=\w)', text)
        
        # Group parts to form reasonable chunks
        sentences = []
        current = ""
        for part in parts:
            if len(current + " " + part) <= 200:  # Smaller sub-chunks
                current = current + (" " if current else "") + part
            else:
                if current:
                    sentences.append(current)
                current = part
        if current:
            sentences.append(current)
    
    return [s.strip() for s in sentences if s.strip()]


def add_to_chroma(chunks: list[Document]):
    # Load the existing database.
    db = Chroma(
        persist_directory=CHROMA_PATH, embedding_function=get_embedding_function()
    )

    # Calculate Page IDs.
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Add or Update the documents.
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only add documents that don't exist in the DB.
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
        db.persist()
    else:
        print("No new documents to add")


def calculate_chunk_ids(chunks):
    # This will create IDs like "data/monopoly.pdf:6:2:1"
    # Format: Source : Page Number : Paragraph Number : Chunk Index

    # Track the last combination to generate sequential chunk indices
    last_para_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        paragraph_num = chunk.metadata.get("paragraph_num", 1)
        
        # Convert page to 1-based indexing (PyPDF uses 0-based)
        page_number = page + 1 if isinstance(page, int) else page
        
        # Create paragraph-level ID
        current_para_id = f"{source}:{page_number}:{paragraph_num}"

        # If the paragraph ID is the same as the last one, increment the chunk index
        if current_para_id == last_para_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 1  # Start at 1 for each new paragraph

        # Calculate the chunk ID in the new format
        chunk_id = f"{current_para_id}:{current_chunk_index}"
        last_para_id = current_para_id

        # Add it to the chunk metadata
        chunk.metadata["id"] = chunk_id
        chunk.metadata["paragraph_id"] = current_para_id
        chunk.metadata["page"] = page_number  # Store the corrected 1-based page number

    return chunks


def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)


if __name__ == "__main__":
    main()