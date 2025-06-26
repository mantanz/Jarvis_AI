
import argparse
import re
from langchain_community.vectorstores.chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama

# New imports for our refactored code
from citation_manager import CitationManager
from citation_models import RenumberedCitation
from get_embedding_function import get_embedding_function

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context. Provide a detailed answer which is complete and covers the topics of the context while being only answering through the context provided. 
When making claims or statements, include inline citations using the format [Source X], where X is the source number provided.

CRITICAL INSTRUCTIONS:
- CAREFULLY READ AND ANALYZE ALL SOURCES PROVIDED before concluding anything
- Check every single source thoroughly for relevant information
- Look for variations in terminology (e.g., "H11", "hypothesis 11", "hypothesis H11", etc.)
- Do not conclude "cannot be determined" unless you have genuinely checked ALL sources

You must strictly follow these citation rules:

1. CRITICAL: Every single factual claim, definition, or piece of information must include an inline citation in the format [Source X].
2. IMPORTANT: The response should indicate exactly the source the fact was taken from.
3. If you use information from multiple sources in one sentence, you MUST cite ALL relevant sources like [Source 1][Source 3].4. Do not combine information from different sources without citing each source separately.
4. VERY IMPORTANT: Do not refer to source numbers in the body of the sentence. For example, write "The lion is the king of the jungle[Source 1]," not "Source 1 states that the lion is the king of the jungle."
5. CRITICAL:  Do not say "according to Source X" or "Source X says." The citation should come only at the end of the sentence or clause, not embedded in the sentence.
6. If no source/context that has been provided supports the claim, say "The answer cannot be determined from the given sources." Never mention the sources or that sources were provided if the answer cannot be determined from the given sources.
7. Be extremely careful not to make any statement without proper citation - even if it seems obvious or general knowledge, if it appears in the context, it must be cited.

--- 

Context:
{context}

--- 

Answer the question based on the above context:  
{question}

"""

def format_response_with_tooltips(response_text: str, citations: list[RenumberedCitation]) -> str:
    """
    Format response text with HTML-style tooltip attributes for web display.
    This function adds data attributes that can be used by frontend tooltip libraries.
    """
    formatted_response = response_text
    for citation in citations:
        escaped_tooltip = citation.content.replace('"', '"').replace("'", "'")
        tooltip_span = f'<span class="citation-tooltip" data-tooltip="{escaped_tooltip}" title="{escaped_tooltip}">[Source {citation.new_source_num}]</span>'
        # Important: Match the exact renumbered citation string
        formatted_response = re.sub(
            f'\[Source {citation.new_source_num}\]',
            tooltip_span,
            formatted_response
        )
    return formatted_response

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    parser.add_argument("--html", action="store_true", help="Output HTML with tooltips")
    parser.add_argument("--show-tooltips", action="store_true", help="Show tooltip data")
    args = parser.parse_args()
    query_text = args.query_text
    
    result = query_rag(query_text)

    if args.html:
        print("HTML Response with Tooltips:")
        print(result["html_response_with_tooltips"])
    elif args.show_tooltips:
        print("Response with Citation Details:")
        print(result["formatted_response"])
        print("\nTooltip Information:")
        for citation in result["citations"]:
            print(f"\n[Source {citation.new_source_num}] Tooltip (from original Source {citation.original_source_num}):")
            print(citation.content)
    else:
        print(result["formatted_response"])

def enhance_query_for_search(query_text: str) -> list[str]:
    """
    Enhance user queries by generating multiple search variations for better semantic matching.
    """
    import re
    
    # Create multiple query variations
    queries = [query_text]  # Always include original query
    
    # Extract key terms and create focused queries
    lower_query = query_text.lower()
    
    # Handle specific acronyms and programs
    if "darpa" in lower_query and "ace" in lower_query:
        queries.extend([
            "DARPA ACE Air Combat Evolution",
            "DARPA ACE program",
            "Air Combat Evolution program",
            "DARPA Air Combat Evolution"
        ])
    
    # Handle common question patterns
    if lower_query.startswith("what is") or lower_query.startswith("what does"):
        # Extract the main subject after "what is/does"
        match = re.search(r"what (?:is|does) (.+?)(?:\?|$)", lower_query)
        if match:
            subject = match.group(1).strip()
            queries.append(subject)
            queries.append(f"{subject} program")
            queries.append(f"{subject} system")
    
    # Handle "how does" questions
    if lower_query.startswith("how does") or lower_query.startswith("how do"):
        match = re.search(r"how (?:does|do) (.+?)(?:\?|$)", lower_query)
        if match:
            subject = match.group(1).strip()
            queries.append(subject)
    
    return queries

def query_rag(query_text: str, selected_documents: list = None):
    # Prepare the DB.
    embedding_function = get_embedding_function()
    try:
        db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    except Exception as e:
        # If there's a tenant issue, try recreating the database
        import os
        import shutil
        if "tenant" in str(e).lower():
            if os.path.exists(CHROMA_PATH):
                shutil.rmtree(CHROMA_PATH)
            # Try creating a fresh database
            db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
        else:
            raise e
    k_chunks = 5

    # Enhanced search with multiple query variations
    enhanced_queries = enhance_query_for_search(query_text)
    all_results = []
    
    # Search with each query variation and collect results
    for query_variant in enhanced_queries:
        variant_results = db.similarity_search_with_score(query_variant, k=k_chunks)
        all_results.extend(variant_results)
    
    # Remove duplicates and sort by score (lower is better)
    seen_content = set()
    unique_results = []
    for doc, score in all_results:
        content_hash = hash(doc.page_content)
        if content_hash not in seen_content:
            seen_content.add(content_hash)
            unique_results.append((doc, score))
    
    # Sort by score and take top k_chunks
    results = sorted(unique_results, key=lambda x: x[1])[:k_chunks]
    
    # Filter results by selected documents if specified
    if selected_documents:
        filtered_results = []
        for doc, score in results:
            # Extract filename from document metadata
            doc_source = doc.metadata.get('source', '')
            # Get just the filename from the path
            filename = doc_source.split('/')[-1] if doc_source else ''
            
            if filename in selected_documents:
                filtered_results.append((doc, score))
        
        results = filtered_results

    # --- REFACTORED SECTION START ---
    
    # 1. Initialize the manager to handle all citation logic
    citation_manager = CitationManager(results, k_chunks)

    # 2. Get the formatted context for the LLM
    context_text = citation_manager.get_llm_context()

    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    model = Ollama(model="llama3.2:latest")
    response_text = model.invoke(prompt)

    # 3. Process the response to get renumbered text and used citations
    processed_response = citation_manager.process_response(response_text)

    # 4. Format the final output based on the structured result
    if processed_response.used_citations:
        # Create the simple citation list for text display
        citation_list = "\n\nSources:\n"
        for citation in processed_response.used_citations:
            citation_list += f"[Source {citation.new_source_num}] {citation.filename}, p. {citation.page}\n"
        
        formatted_response = f"{processed_response.renumbered_response_text}{citation_list}"
        
        # Create the HTML version with tooltips
        html_response = format_response_with_tooltips(
            processed_response.renumbered_response_text, 
            processed_response.used_citations
        )
        
        # Convert RenumberedCitation objects to dictionaries for Streamlit compatibility
        citations_dict = []
        for citation in processed_response.used_citations:
            citations_dict.append({
                "source_num": citation.new_source_num,
                "original_source_num": citation.original_source_num,
                "filename": citation.filename,
                "page": citation.page,
                "tooltip_text": citation.content,
                "relevance_score": citation.relevance_score
            })
        
        # Add navigation enhancement (new functionality)
        try:
            from citation_navigation import CitationNavigation
            nav_handler = CitationNavigation()
            enhanced_citations = nav_handler.enhance_citations_with_navigation(citations_dict)
        except ImportError:
            # Fallback to original citations if navigation module not available
            enhanced_citations = citations_dict
        
        return {
            "response_text": processed_response.renumbered_response_text,
            "citations": citations_dict,
            "enhanced_citations": enhanced_citations,  # New field with navigation data
            "formatted_response": formatted_response,
            "html_response_with_tooltips": html_response,
            "context_used": context_text,
            "total_citations_used": len(processed_response.used_citations)
        }
    else:
        # Handle case where no sources were cited
        return {
            "response_text": response_text,
            "citations": [],
            "formatted_response": f"{response_text}\n\n(No sources cited)",
            "html_response_with_tooltips": response_text,
            "context_used": context_text,
            "total_citations_used": 0
        }
    # --- REFACTORED SECTION END ---

if __name__ == "__main__":
    main()