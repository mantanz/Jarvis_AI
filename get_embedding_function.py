from langchain_community.embeddings import HuggingFaceEmbeddings

def get_embedding_function():
    # Return sentence-transformers/all-MiniLM-L6-v2 embeddings
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")