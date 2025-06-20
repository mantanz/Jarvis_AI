
# import argparse
# from langchain.vectorstores.chroma import Chroma
# from langchain.prompts import ChatPromptTemplate
# from langchain_community.llms.ollama import Ollama
# import re

# from get_embedding_function import get_embedding_function
# from citation_utils import strip_html_tags

# CHROMA_PATH = "chroma"


# def format_response_with_tooltips(response_text: str, citations: list) -> str:
#     """
#     Format response text with HTML-style tooltip attributes for web display.
#     This function adds data attributes that can be used by frontend tooltip libraries.
#     """
#     formatted_response = response_text
    
#     # Create a mapping of citation numbers to tooltip data
#     citation_tooltips = {}
#     for citation in citations:
#         citation_tooltips[citation["source_num"]] = citation["tooltip_text"]
    
#     # Replace citations with tooltip-enabled spans
#     for source_num, tooltip_text in citation_tooltips.items():
#         # Escape quotes in tooltip text for HTML attributes
#         escaped_tooltip = tooltip_text.replace('"', '&quot;').replace("'", "&#39;")
        
#         # Replace [Source X] with tooltip-enabled span
#         tooltip_span = f'<span class="citation-tooltip" data-tooltip="{escaped_tooltip}" title="{escaped_tooltip}">[Source {source_num}]</span>'
#         formatted_response = re.sub(
#             f'\[Source {source_num}\]',
#             tooltip_span,
#             formatted_response
#         )
    
#     return formatted_response

# PROMPT_TEMPLATE = """
# Answer the question based only on the following context. Provide a detailed answer which is complete and covers the topics of the context while being only answering through the context provided. 
# When making claims or statements, include inline citations using the format [Source X], where X is the source number provided.

# You must strictly follow these citation rules:

# 1. All factual claims must include an inline citation in the format [Source X].
# 2. Do not refer to source numbers in the body of the sentence. For example, write "The lion is the king of the jungle[Source 1]," not "Source 1 states that the lion is the king of the jungle."
# 3. Do not say "according to Source X" or "Source X says." The citation should come only at the end of the sentence or clause, not embedded in the sentence.
# 4. If a sentence includes multiple facts from different sources, include all relevant citations like [Source 1], [Source 3].
# 5. If no source supports the claim, say "The answer cannot be determined from the given sources." Never mention the sources or that sources were provided if the answer cannot be determined from the given sources.

# --- 

# Context:
# {context}

# --- 

# Answer the question based on the above context:  
# {question}

# """


# def main():
#     # Create CLI.
#     parser = argparse.ArgumentParser()
#     parser.add_argument("query_text", type=str, help="The query text.")
#     parser.add_argument("--html", action="store_true", help="Output HTML with tooltips")
#     parser.add_argument("--show-tooltips", action="store_true", help="Show tooltip data")
#     args = parser.parse_args()
#     query_text = args.query_text
#     result = query_rag(query_text)
    
#     if args.html:
#         print("HTML Response with Tooltips:")
#         print(result["html_response_with_tooltips"])
#     elif args.show_tooltips:
#         print("Response with Citation Details:")
#         print(result["formatted_response"])
#         print("\nTooltip Information:")
#         for citation in result["citations"]:
#             print(f"\n[Source {citation['source_num']}] Tooltip:")
#             print(citation["tooltip_text"])
#     else:
#         print(result["formatted_response"])


# def query_rag(query_text: str):
#     # Prepare the DB.
#     embedding_function = get_embedding_function()
#     db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

#     # Configure number of chunks to retrieve (can be changed in future)
#     k_chunks = 5

#     # Search the DB.
#     results = db.similarity_search_with_score(query_text, k=k_chunks)

#     # Build context with source numbers
#     context_parts = []
#     all_citations = []
    
#     for i, (doc, score) in enumerate(results, 1):
#         # Extract source information
#         source_id = doc.metadata.get("id", "Unknown")
#         source_parts = source_id.split(":")
        
#         if len(source_parts) >= 2:
#             file_path = source_parts[0]
#             page_num = source_parts[1]
#             filename = file_path.split("/")[-1] if "/" in file_path else file_path
#         else:
#             filename = "Unknown Document"
#             page_num = "Unknown"
        
#         # Clean HTML tags from document content
#         clean_content = strip_html_tags(doc.page_content)
        
#         # Add numbered context
#         context_parts.append(f"[Source {i}] {clean_content}")
        
#         # Store all citation info with detailed tooltip data
#         all_citations.append({
#             "source_num": i,
#             "filename": filename,
#             "page": page_num,
#             "source_id": source_id,
#             "full_file_path": file_path,
#             "relevance_score": round(1 - score, 3) if score else "N/A",  # Convert distance to similarity
#             "content_preview": clean_content[:200] + "..." if len(clean_content) > 200 else clean_content,
#             "full_content": clean_content,
#             "tooltip_text": clean_content  # Show only the full document content
#         })
    
#     context_text = "\n\n---\n\n".join(context_parts)
#     prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
#     prompt = prompt_template.format(context=context_text, question=query_text)

#     model = Ollama(model="llama3.2:latest")
#     response_text = model.invoke(prompt)

#     # Extract which sources are cited in the response (both formats)
#     cited_sources_brackets = re.findall(r'\[Source (\d+)\]', response_text)
#     cited_sources_parens = re.findall(r'\(Source (\d+)\)', response_text)
    
#     # Combine both formats and get all cited source numbers (preserving order)
#     all_cited = cited_sources_brackets + cited_sources_parens
#     cited_source_nums = [int(num) for num in all_cited]
    
#     # Filter to only valid citations (within our chunk range 1 to k_chunks)
#     valid_citation_nums = [num for num in cited_source_nums if 1 <= num <= k_chunks]
    
#     # Get unique valid citations in ORDER OF FIRST APPEARANCE (not numerical order)
#     unique_valid_citations = []
#     seen = set()
#     for num in valid_citation_nums:
#         if num not in seen:
#             unique_valid_citations.append(num)
#             seen.add(num)
    
#     # Filter citations to only include valid ones and sort by ORDER OF FIRST APPEARANCE
#     used_citations = []
#     for source_num in unique_valid_citations:  # This preserves appearance order
#         citation = next(c for c in all_citations if c["source_num"] == source_num)
#         used_citations.append(citation)

#     # FRONTEND RENUMBERING: Create mapping from original numbers to sequential 1, 2, 3...
#     if used_citations:
#         # Create mapping: {original_num: new_num}
#         renumber_map = {}
#         for new_num, citation in enumerate(used_citations, 1):
#             original_num = citation["source_num"]
#             renumber_map[original_num] = new_num
        
#         # Replace citation numbers in response text using temporary placeholders to avoid conflicts
#         renumbered_response = response_text
        
#         # Step 1: Replace with temporary placeholders first
#         for original_num, new_num in renumber_map.items():
#             # Use unique temporary placeholders that won't conflict
#             temp_placeholder_brackets = f"__TEMP_SOURCE_{original_num}_BRACKETS__"
#             temp_placeholder_parens = f"__TEMP_SOURCE_{original_num}_PARENS__"
            
#             renumbered_response = re.sub(
#                 f'\[Source {original_num}\]',
#                 temp_placeholder_brackets,
#                 renumbered_response
#             )
#             renumbered_response = re.sub(
#                 f'\(Source {original_num}\)',
#                 temp_placeholder_parens,
#                 renumbered_response
#             )
        
#         # Step 2: Replace temporary placeholders with final numbers
#         for original_num, new_num in renumber_map.items():
#             temp_placeholder_brackets = f"__TEMP_SOURCE_{original_num}_BRACKETS__"
#             temp_placeholder_parens = f"__TEMP_SOURCE_{original_num}_PARENS__"
            
#             renumbered_response = renumbered_response.replace(
#                 temp_placeholder_brackets,
#                 f'[Source {new_num}]'
#             )
#             renumbered_response = renumbered_response.replace(
#                 temp_placeholder_parens,
#                 f'(Source {new_num})'
#             )
        
#         # Remove any invalid citations from the response text (outside our range)
#         for i in range(k_chunks + 1, k_chunks + 20):  # Remove citations beyond our range
#             renumbered_response = re.sub(f'\[Source {i}\]', '', renumbered_response)
#             renumbered_response = re.sub(f'\(Source {i}\)', '', renumbered_response)
        
#         # Update citation objects with new numbers for display
#         renumbered_citations = []
#         for new_num, citation in enumerate(used_citations, 1):
#             renumbered_citation = citation.copy()
#             renumbered_citation["source_num"] = new_num
#             renumbered_citation["original_source_num"] = citation["source_num"]  # Keep track of original
#             # Keep the same tooltip text (full document content only)
#             renumbered_citation["tooltip_text"] = citation["tooltip_text"]
#             renumbered_citations.append(renumbered_citation)
        
#         # Format simple citations with new numbers
#         citation_list = "\n\nSources:\n"
#         for citation in renumbered_citations:
#             citation_list += f"[Source {citation['source_num']}] {citation['filename']}, p. {citation['page']}\n"
        
#         formatted_response = f"{renumbered_response}{citation_list}"
#         html_response_with_tooltips = format_response_with_tooltips(renumbered_response, renumbered_citations)
        
#         return {
#             "response_text": renumbered_response,
#             "citations": renumbered_citations,  # Return renumbered citations
#             "formatted_response": formatted_response,
#             "html_response_with_tooltips": html_response_with_tooltips,
#             "context_used": context_text,
#             "total_available_chunks": k_chunks,
#             "total_citations_used": len(renumbered_citations)
#         }
#     else:
#         citation_list = "\n\n(No sources cited)"
#         formatted_response = f"{response_text}{citation_list}"
        
#         return {
#             "response_text": response_text,
#             "citations": [],
#             "formatted_response": formatted_response,
#             "context_used": context_text,
#             "total_available_chunks": k_chunks,
#             "total_citations_used": 0
#         }


# if __name__ == "__main__":
#     main()


# query.py

import argparse
import re
from langchain.vectorstores.chroma import Chroma
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

You must strictly follow these citation rules:

1. CRITICAL: Every single factual claim, definition, or piece of information must include an inline citation in the format [Source X]. 
2. IMPORTANT: The response should indicate exactly the source the fact was taken from.
3. If you use information from multiple sources in one sentence, you MUST cite ALL relevant sources like [Source 1][Source 3].4. Do not combine information from different sources without citing each source separately.
4. VERY IMPORTANT: Do not refer to source numbers in the body of the sentence. For example, write "The lion is the king of the jungle[Source 1]," not "Source 1 states that the lion is the king of the jungle."
5. Do not say "according to Source X" or "Source X says." The citation should come only at the end of the sentence or clause, not embedded in the sentence.
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

def query_rag(query_text: str):
    # Prepare the DB.
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    k_chunks = 5

    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=k_chunks)

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
        
        return {
            "response_text": processed_response.renumbered_response_text,
            "citations": citations_dict,
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