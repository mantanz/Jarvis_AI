# """
# Simple citation utilities for RAG system.
# Provides basic functions for citation validation and text processing.
# """

# import re
# from typing import List, Dict, Any

# def extract_citations_from_text(text: str) -> List[str]:
#     """Extract all citation references from generated text (strict format: only [Source X] and (Source X))."""
#     # Only match properly formatted citations, ignore plain "Source X" text
#     pattern_brackets = r'\[Source \d+\]'
#     pattern_parens = r'\(Source \d+\)'
    
#     brackets_citations = re.findall(pattern_brackets, text)
#     parens_citations = re.findall(pattern_parens, text)
    
#     return brackets_citations + parens_citations

# def validate_citations(response_text: str, available_citations: List[Dict[str, Any]]) -> Dict[str, Any]:
#     """
#     Validate that all citations in the response text are valid.
#     Only counts properly formatted citations ([Source X] or (Source X)).
    
#     Returns:
#         Dictionary with validation results
#     """
#     cited_sources = extract_citations_from_text(response_text)
    
#     # Create available source references in both formats
#     available_source_refs = []
#     for citation in available_citations:
#         source_num = citation['source_num']
#         available_source_refs.extend([
#             f"[Source {source_num}]",
#             f"(Source {source_num})"
#         ])
    
#     valid_citations = [cite for cite in cited_sources if cite in available_source_refs]
#     invalid_citations = [cite for cite in cited_sources if cite not in available_source_refs]
    
#     return {
#         "total_citations": len(cited_sources),
#         "valid_citations": len(valid_citations),
#         "invalid_citations": len(invalid_citations),
#         "citation_coverage": len(valid_citations) / len(cited_sources) if cited_sources else 0,
#         "missing_citations": invalid_citations
#     } 

import re
from typing import List, Dict, Any

def strip_html_tags(text: str) -> str:
    """
    Remove HTML tags from text and clean up common HTML entities.
    
    Args:
        text: Text that may contain HTML tags and entities
        
    Returns:
        Clean text with HTML tags removed
    """
    if not text:
        return text
    
    # Remove HTML tags
    clean_text = re.sub(r'<[^>]+>', '', text)
    
    # Replace common HTML entities
    html_entities = {
        '&nbsp;': ' ',
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&#39;': "'",
        '&apos;': "'",
        '&hellip;': '...',
        '&mdash;': '—',
        '&ndash;': '–',
        '&rsquo;': "'",
        '&lsquo;': "'",
        '&rdquo;': '"',
        '&ldquo;': '"'
    }
    
    for entity, replacement in html_entities.items():
        clean_text = clean_text.replace(entity, replacement)
    
    # Clean up extra whitespace
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    return clean_text

def clean_text_for_processing(text: str, strip_html: bool = True) -> str:
    """
    General text cleaning utility for RAG processing.
    
    Args:
        text: Input text to clean
        strip_html: Whether to remove HTML tags (default: True)
        
    Returns:
        Cleaned text ready for processing
    """
    if not text:
        return text
    
    if strip_html:
        text = strip_html_tags(text)
    
    # Additional cleaning can be added here as needed
    return text

def extract_citations_from_text(text: str) -> List[str]:
    """
    Extract all citation references from generated text:
    - [Source X]
    - (Source X)
    - Source X (plain, no brackets)
    
    Here X can be any string without brackets/parentheses (like numbers or IDs).
    """
    pattern_brackets = r'\[Source [^\]]+\]'
    pattern_parens = r'\(Source [^)]+\)'
    pattern_plain = r'(?<![\[\(])\bSource [^\s\[\]\(\)]+'
    # Explanation:
    # (?<![\[\(]) ensures Source X is NOT preceded by [ or ( to avoid double counting
    
    brackets_citations = re.findall(pattern_brackets, text)
    parens_citations = re.findall(pattern_parens, text)
    plain_citations = re.findall(pattern_plain, text)
    
    # Combine all and remove duplicates while preserving order
    seen = set()
    citations = []
    for c in brackets_citations + parens_citations + plain_citations:
        if c not in seen:
            seen.add(c)
            citations.append(c)
    return citations


def normalize_citation(citation: str) -> str:
    """
    Normalize citation to a canonical form, e.g. "Source 5"
    Removes brackets or parentheses.
    """
    # Remove brackets or parentheses and strip whitespace
    return re.sub(r'[\[\]\(\)]', '', citation).strip()


def validate_citations(response_text: str, available_citations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate that all citations in the response text are valid.
    Handles bracketed, parenthesized, and plain citations like 'Source 5'.
    
    available_citations should have 'source_id' or 'source_num' keys matching normalized citation texts.
    """
    cited_sources = extract_citations_from_text(response_text)
    
    # Normalize cited sources to compare
    normalized_cited = [normalize_citation(c) for c in cited_sources]
    
    # Build a set of normalized available citation references
    available_refs = set()
    for citation in available_citations:
        # Adjust key name as needed ('source_num' or 'source_id')
        source = citation.get('source_num') or citation.get('source_id')
        if source is None:
            continue
        # Normalize just in case
        available_refs.add(f"Source {source}".strip())
    
    valid = [c for c in normalized_cited if c in available_refs]
    invalid = [c for c in normalized_cited if c not in available_refs]
    
    coverage = len(valid) / len(normalized_cited) if normalized_cited else 0
    
    return {
        "total_citations": len(normalized_cited),
        "valid_citations": len(valid),
        "invalid_citations": len(invalid),
        "citation_coverage": coverage,
        "invalid_citations_list": invalid
    }
