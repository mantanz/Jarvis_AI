
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
    # Custom paragraph-aware text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
        # Add paragraph separators as primary split points
        separators=["\n\n", "\n"]  # Prioritize paragraph breaks
    )
    
    chunks = []
    
    for doc in documents:
        # First, split the document into paragraphs
        paragraphs = doc.page_content.split('\n\n')
        
        # Process each paragraph separately to maintain paragraph boundaries
        for para_idx, paragraph in enumerate(paragraphs, 1):
            if not paragraph.strip():  # Skip empty paragraphs
                continue
                
            # Create a temporary document for this paragraph
            para_doc = Document(
                page_content=paragraph,
                metadata={
                    **doc.metadata,
                    "paragraph_num": para_idx
                }
            )
            
            # Split the paragraph into chunks if it's too long
            para_chunks = text_splitter.split_documents([para_doc])
            
            # If paragraph fits in one chunk, keep it as is
            if len(para_chunks) == 1:
                chunks.append(para_chunks[0])
            else:
                # If paragraph needs to be split, add chunk numbers within the paragraph
                for chunk_idx, chunk in enumerate(para_chunks):
                    chunk.metadata["chunk_in_paragraph"] = chunk_idx + 1
                    chunks.append(chunk)
    
    return chunks


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
        
        # Create paragraph-level ID
        current_para_id = f"{source}:{page}:{paragraph_num}"

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

    return chunks


def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)


if __name__ == "__main__":
    main()