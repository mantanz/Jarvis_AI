# citation_manager.py

import re
from typing import List, Tuple
from langchain_core.documents import Document

from citation_models import Citation, RenumberedCitation, ProcessedLLMResponse
from citation_utils import strip_html_tags # Assuming you have this helper

class CitationManager:
    """
    Manages the creation, formatting, and processing of citations for the RAG pipeline.
    """
    def __init__(self, search_results: List[Tuple[Document, float]], k_chunks: int):
        self.k_chunks = k_chunks
        self.all_citations: List[Citation] = self._create_initial_citations(search_results)
        self.lookup = {c.source_num: c for c in self.all_citations}

    def _create_initial_citations(self, search_results: List[Tuple[Document, float]]) -> List[Citation]:
        """Creates the initial list of Citation objects from ChromaDB results."""
        citations = []
        for i, (doc, score) in enumerate(search_results, 1):
            source_id = doc.metadata.get("id", "Unknown")
            source_parts = source_id.split(":")
            
            if len(source_parts) >= 2:
                file_path, page_num = source_parts[0], source_parts[1]
                filename = file_path.split("/")[-1] if "/" in file_path else file_path
            else:
                filename, page_num = "Unknown Document", "N/A"
            
            clean_content = strip_html_tags(doc.page_content)
            
            citations.append(
                Citation(
                    source_num=i,
                    filename=filename,
                    page=page_num,
                    source_id=source_id,
                    relevance_score=round(1 - score, 3) if score is not None else None,
                    content=clean_content
                )
            )
        return citations

    def get_llm_context(self) -> str:
        """Formats the context string to be passed to the LLM."""
        context_parts = [f"[Source {c.source_num}] {c.content}" for c in self.all_citations]
        return "\n\n---\n\n".join(context_parts)

    def process_response(self, response_text: str) -> ProcessedLLMResponse:
        """
        Parses the LLM response, identifies used citations, renumbers them,
        and returns a structured result.
        """
        # Find all cited source numbers, preserving order of appearance
        cited_nums_str = re.findall(r'\[Source (\d+)\]', response_text)
        cited_original_nums = [int(num) for num in cited_nums_str]
        
        # Get unique, valid citations in order of first appearance
        used_citations_ordered = []
        seen = set()
        for num in cited_original_nums:
            if num not in seen and 1 <= num <= self.k_chunks:
                seen.add(num)
                used_citations_ordered.append(self.lookup[num])

        if not used_citations_ordered:
            return ProcessedLLMResponse(renumbered_response_text=response_text, used_citations=[])

        # Create a mapping from original numbers to new sequential numbers (1, 2, 3...)
        renumber_map = {citation.source_num: new_num for new_num, citation in enumerate(used_citations_ordered, 1)}

        # Renumber the response text using a safe, two-step replacement
        renumbered_text = response_text
        
        # Step 1: Replace valid citations with temporary, unique placeholders
        for original_num, new_num in renumber_map.items():
            renumbered_text = re.sub(
                f'\[Source {original_num}\]', 
                f"__TEMP_SOURCE_{new_num}__", 
                renumbered_text
            )
        
        # Step 2: Remove any remaining invalid citations (outside our valid range)
        # This handles cases where LLM generates citations beyond k_chunks
        for num in cited_original_nums:
            if num < 1 or num > self.k_chunks:
                renumbered_text = re.sub(f'\[Source {num}\]', '', renumbered_text)
        
        # Step 2.5: Remove original citations from source documents (like [23], [12], etc.)
        # These are citations that existed in the original documents, not our RAG citations
        renumbered_text = re.sub(r'\[(\d+)\]', '', renumbered_text)
        
        # Step 3: Replace placeholders with final, renumbered citation format
        for original_num, new_num in renumber_map.items():
            renumbered_text = re.sub(
                f"__TEMP_SOURCE_{new_num}__",
                f"[Source {new_num}]",
                renumbered_text
            )
        
        # Step 4: Clean up any extra whitespace left by removed citations
        renumbered_text = re.sub(r'\s+', ' ', renumbered_text).strip()
        
        # Create the final list of renumbered citation objects
        final_citations = []
        for new_num, original_citation in enumerate(used_citations_ordered, 1):
            final_citations.append(
                RenumberedCitation(
                    new_source_num=new_num,
                    original_source_num=original_citation.source_num,
                    filename=original_citation.filename,
                    page=original_citation.page,
                    relevance_score=original_citation.relevance_score,
                    content=original_citation.content
                )
            )
        
        return ProcessedLLMResponse(
            renumbered_response_text=renumbered_text,
            used_citations=final_citations
        )