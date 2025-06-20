# citation_models.py

from pydantic import BaseModel, Field
from typing import Optional, List

class Citation(BaseModel):
    """
    Represents a single piece of context retrieved from the vector database,
    before being processed by the LLM.
    """
    source_num: int = Field(..., description="The original source number (1-k) assigned to this chunk.")
    filename: str = Field(..., description="The name of the source document.")
    page: str = Field(..., description="The page number of the source document.")
    source_id: str = Field(..., description="The unique ID from the vector database (e.g., 'file.pdf:page_num').")
    relevance_score: Optional[float] = Field(None, description="Similarity score (0-1) from the vector search.")
    content: str = Field(..., description="The full, clean text content of the chunk, used for tooltips and context.")

class RenumberedCitation(BaseModel):
    """
    Represents a citation that was actually used by the LLM in its response,
    with its source number remapped to be sequential (1, 2, 3...).
    """
    new_source_num: int = Field(..., description="The new, sequential source number for final display.")
    original_source_num: int = Field(..., description="The original source number (1-k) this corresponded to.")
    filename: str
    page: str
    relevance_score: Optional[float]
    content: str

class ProcessedLLMResponse(BaseModel):
    """
    A structured object containing the final, processed results after the LLM call.
    """
    renumbered_response_text: str = Field(..., description="The LLM's response with citation numbers remapped sequentially.")
    used_citations: List[RenumberedCitation] = Field(..., description="A list of the citation objects that were actually used.")