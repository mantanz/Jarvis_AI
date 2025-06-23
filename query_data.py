
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