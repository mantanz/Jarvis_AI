import streamlit as st
from processing import load_documents, split_documents, add_to_chroma, clear_database
from query_data import query_rag
import json
import urllib.parse

st.set_page_config(page_title="RAG Pipeline App", page_icon="📚")

# Custom CSS for citations with chunk navigation
st.markdown("""
<style>
    .citation-clickable {
        background-color: #e6f3ff;
        border: 1px solid #0066cc;
        border-radius: 3px;
        padding: 2px 6px;
        cursor: pointer;
        position: relative;
        text-decoration: none;
        color: #0066cc;
        font-weight: bold;
        display: inline-block;
        margin: 0 2px;
        transition: all 0.2s ease;
    }

    .citation-clickable:hover {
        background-color: #cce6ff;
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0,102,204,0.2);
    }

    /* Tooltip container */
    .tooltip {
        position: relative;
        display: inline-block;
    }

    /* Tooltip text */
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 400px;
        max-width: 90vw;
        max-height: 300px;
        background-color: #333;
        color: #fff;
        text-align: left;
        border-radius: 6px;
        padding: 15px;
        position: absolute;
        z-index: 1000;
        bottom: 125%;
        left: 50%;
        margin-left: -200px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 12px;
        line-height: 1.5;
        white-space: pre-wrap;
        overflow-y: auto;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        pointer-events: none;
        word-wrap: break-word;
    }

    /* Tooltip arrow */
    .tooltip .tooltiptext::after {
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: #333 transparent transparent transparent;
    }

    /* Show tooltip on hover */
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .tooltip .tooltiptext {
            width: 350px;
            margin-left: -175px;
            max-height: 250px;
        }
    }
    
    @media (max-width: 480px) {
        .tooltip .tooltiptext {
            width: 300px;
            margin-left: -150px;
            max-height: 200px;
            font-size: 11px;
        }
    }

    /* Streamlit specific adjustments */
    .stChatMessage .tooltip {
        display: inline-block;
    }

    /* Prevent tooltip from being cut off by containers */
    .stChatMessage {
        overflow: visible !important;
    }

    /* Document viewer section */
    .document-viewer-section {
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        margin: 10px 0;
        background: #f8f9fa;
    }

    .document-viewer-header {
        background: #2196f3;
        color: white;
        padding: 10px 15px;
        margin: 0;
        border-radius: 6px 6px 0 0;
        font-weight: bold;
    }
</style>

<script>
// Global variable to track currently displayed document viewer
let currentDocumentViewer = null;

// Function to navigate to chunk in PDF viewer
function navigateToChunk(sourceNum) {
    // Find the iframe containing the PDF viewer
    const pdfViewerIframes = document.querySelectorAll('iframe[title*="stIFrame"]');
    
    pdfViewerIframes.forEach(iframe => {
        try {
            // Send message to PDF viewer to navigate to chunk
            iframe.contentWindow.postMessage({
                type: 'navigateToChunk',
                chunkId: 'chunk-' + sourceNum
            }, '*');
        } catch (e) {
            // Cross-origin restrictions, but message should still get through
        }
    });
}

// Add event listener for citation clicks
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('citation-clickable')) {
        const sourceNum = event.target.getAttribute('data-source-num');
        if (sourceNum) {
            navigateToChunk(sourceNum);
        }
    }
});
</script>
""", unsafe_allow_html=True)

st.title("RAG Pipeline")

# Add info about the new document viewer feature


st.markdown("---")


def format_response_with_chunk_navigation(response_text: str, citations: list) -> str:
    """
    Format response text with clickable citations and tooltips.
    """
    import re
    
    formatted_response = response_text
    
    # Create a mapping of citation numbers to citation data
    citation_data = {}
    for citation in citations:
        citation_data[citation["source_num"]] = citation
    
    # Replace citations with tooltip-enabled spans (no click navigation needed here)
    for source_num, citation in citation_data.items():
        # Format tooltip text
        formatted_tooltip = (citation["tooltip_text"]
                           .replace('\n\n', ' • ')  # Paragraph breaks become bullet points
                           .replace('\n', ' ')       # Single line breaks become spaces
                           .replace('\r', ' '))
        
        # Escape quotes for HTML attributes
        escaped_tooltip = (formatted_tooltip
                          .replace('"', '&quot;')
                          .replace("'", "&#39;"))
        
        # Create citation with tooltip (navigation will be via buttons in sources section)
        citation_html = f'''<span class="tooltip citation-clickable" style="cursor: help;">[Source {source_num}]<span class="tooltiptext">{escaped_tooltip}</span></span>'''
        
        # Replace [Source X] with citation
        formatted_response = re.sub(
            f'\\[Source {source_num}\\]',
            citation_html,
            formatted_response
        )
    
    return formatted_response

def create_document_viewer_url(filename: str, citations: list, active_source: int = None) -> str:
    """Create URL for standalone document viewer with chunk data."""
    # Prepare chunk data for URL
    chunk_data = []
    for citation in citations:
        if citation.get('filename') == filename:
            chunk_data.append({
                'source_num': citation.get('source_num'),
                'page': citation.get('page'),
                'tooltip_text': citation.get('tooltip_text', '')
            })
    
    # Encode data for URL
    chunks_encoded = urllib.parse.quote(json.dumps(chunk_data))
    
    # Create URL for standalone viewer (runs on port 8503)
    base_url = "http://localhost:8503"
    viewer_url = f"{base_url}/?file={filename}&chunks={chunks_encoded}"
    
    if active_source:
        viewer_url += f"&active=chunk-{active_source}"
    
    return viewer_url

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Section: Ingest PDFs into Vector Store
with st.sidebar:
    st.header("🔧 Document Management")
    
    # if st.button("Clear Vector Store Database"):
    #     clear_database()
    #     st.success("Vector store database cleared!")

    if st.button("Ingest PDFs to Vector Store"):
        with st.spinner("⏳ Loading PDFs and updating vector store..."):
            documents = load_documents()
            chunks = split_documents(documents)
            add_to_chroma(chunks)
        st.success("Document ingestion complete!")
    
    st.markdown("---")
    
    # Chat controls
    st.header("💬 Chat Controls")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    

    
    # Download chat history
    # if st.session_state.messages and st.button("📚 Download Chat"):
    #     history_content = "# Chat History\n\n"
        
    #     for i, message in enumerate(st.session_state.messages):
    #         if message["role"] == "user":
    #             history_content += f"**User:** {message['content']}\n\n"
    #         else:
    #             history_content += f"**Assistant:** {message['content']}\n\n"
    #             if message.get('citations'):
    #                 history_content += "**Sources:**\n"
    #                 for citation in message['citations']:
    #                     history_content += f"- [Source {citation['source_num']}] {citation['filename']}, p. {citation['page']}\n"
    #                 history_content += "\n"
        
    #     st.download_button(
    #         label="Download Chat History",
    #         data=history_content,
    #         file_name="chat_history.md",
    #         mime="text/markdown"
    #     )

# Document opening handler with highlighting
st.components.v1.html("""
<script>
function openDocument(filename, filepath, page, highlightText, fullText) {
    try {
        // Store the highlight information for potential use
        if (highlightText) {
            console.log('Opening document with highlight:', highlightText);
            sessionStorage.setItem('highlightText', highlightText);
            sessionStorage.setItem('fullText', fullText);
        }
        
        // Try different methods to open the document with highlighting
        let fileUrl = 'file:///' + filepath.replace(/\\/g, '/') + '#page=' + page;
        
        // If we have text to highlight, try to use PDF.js search functionality
        if (highlightText) {
            // Try PDF.js viewer URL format with search
            const searchText = encodeURIComponent(highlightText.substring(0, 50));
            const pdfJsUrl = fileUrl + '&search=' + searchText;
            
            // Method 1: Try to open with PDF.js search
            let newWindow = window.open(pdfJsUrl, '_blank');
            
            // Method 2: If that fails, try standard URL
            if (!newWindow || newWindow.closed || typeof newWindow.closed == 'undefined') {
                newWindow = window.open(fileUrl, '_blank');
            }
            
            // Method 3: If that also fails, try creating a temporary link
            if (!newWindow || newWindow.closed || typeof newWindow.closed == 'undefined') {
                const link = document.createElement('a');
                link.href = fileUrl;
                link.target = '_blank';
                link.style.display = 'none';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }
            
            // Show user notification about the highlighted text
            setTimeout(() => {
                if (confirm('Document opened. The highlighted text is: "' + highlightText + '..." \\n\\nClick OK to copy the full text to clipboard for easy finding.')) {
                    navigator.clipboard.writeText(fullText).then(() => {
                        alert('Full text copied to clipboard! You can use Ctrl+F to search for it in the PDF.');
                    }).catch(() => {
                        prompt('Full text to search for (copy this):', fullText);
                    });
                }
            }, 1000);
            
        } else {
            // Standard document opening without highlighting
            const newWindow = window.open(fileUrl, '_blank');
            
            if (!newWindow || newWindow.closed || typeof newWindow.closed == 'undefined') {
                const link = document.createElement('a');
                link.href = fileUrl;
                link.target = '_blank';
                link.style.display = 'none';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }
        }
        
    } catch (error) {
        console.error('Could not open document:', error);
        alert('Could not open document: ' + filename + '. Please check if the file exists and your browser allows file:// URLs.');
    }
}

// Listen for document opening events
window.addEventListener('openDocument', function(event) {
    const { filename, filepath, page, highlightText, fullText } = event.detail;
    openDocument(filename, filepath, page, highlightText, fullText);
});

// Also check for any pending documents to open
setInterval(function() {
    if (window.documentsToOpen && window.documentsToOpen.length > 0) {
        const doc = window.documentsToOpen.shift();
        openDocument(doc.filename, doc.filepath, doc.page, doc.highlightText, doc.fullText);
    }
}, 100);
</script>
""", height=0)

# Main chat interface


# Display chat messages
chat_container = st.container()
with chat_container:
    for msg_idx, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                # Display response with clickable citations for chunk navigation
                if message.get("citations"):
                    response_with_navigation = format_response_with_chunk_navigation(
                        message["content"], 
                        message["citations"]
                    )
                    st.markdown(response_with_navigation, unsafe_allow_html=True)
                else:
                    st.write(message["content"])
                
                # Show expandable sources section with navigation
                if message.get("citations"):
                    with st.expander(f"📚 Sources ({len(message['citations'])} cited)", expanded=False):
                        citations_to_display = message.get("citations", [])
                        
                        # Group citations by filename for better organization
                        citations_by_file = {}
                        for citation in citations_to_display:
                            filename = citation.get('filename', 'Unknown')
                            if filename not in citations_by_file:
                                citations_by_file[filename] = []
                            citations_by_file[filename].append(citation)
                        
                        for filename, file_citations in citations_by_file.items():
                            if filename.endswith('.pdf'):
                                st.markdown(f"**📄 {filename}**")
                                
                                # Create a button to open the document viewer with all citations
                                viewer_url = create_document_viewer_url(filename, file_citations)
                                st.markdown(f'<a href="{viewer_url}" target="_blank" style="text-decoration: none;"><button style="background: #2196f3; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; margin-bottom: 10px;">🔍 Open Document Viewer</button></a>', unsafe_allow_html=True)
                                
                                # List the citations for this file
                                for citation in file_citations:
                                    col1, col2 = st.columns([4, 1])
                                    with col1:
                                        st.write(f"   • **[Source {citation['source_num']}]** Page {citation['page']}")
                                    with col2:
                                        # Button to open viewer focused on this specific citation
                                        focused_url = create_document_viewer_url(filename, file_citations, citation['source_num'])
                                        st.markdown(f'<a href="{focused_url}" target="_blank" style="text-decoration: none;"><button style="background: #ff9800; color: white; border: none; padding: 4px 8px; border-radius: 3px; cursor: pointer; font-size: 12px;">📍 Go to Source</button></a>', unsafe_allow_html=True)
                                
                                st.markdown("---")
                            else:
                                # Non-PDF files
                                for citation in file_citations:
                                    st.write(f"• **[Source {citation['source_num']}]** {citation['filename']}, p. {citation['page']}")

# Chat input
if query := st.chat_input("Ask a question about your documents..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": query})
    
    # Display user message
    with st.chat_message("user"):
        st.write(query)
    
    # Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("⏳ Thinking..."):
            result = query_rag(query)
        
        # Store context for sidebar display
        st.session_state.last_context = result["context_used"]
        
        # Display the response with clickable citations
        if result["citations"]:
            response_with_navigation = format_response_with_chunk_navigation(
                result["response_text"], 
                result["citations"]
            )
            st.markdown(response_with_navigation, unsafe_allow_html=True)
        else:
            st.write(result["response_text"])
        
        # Show expandable sources section with navigation
        if result["citations"]:
            with st.expander(f"📚 Sources ({len(result['citations'])} cited)", expanded=False):
                citations_to_display = result["citations"]
                
                # Group citations by filename
                citations_by_file = {}
                for citation in citations_to_display:
                    filename = citation.get('filename', 'Unknown')
                    if filename not in citations_by_file:
                        citations_by_file[filename] = []
                    citations_by_file[filename].append(citation)
                
                for filename, file_citations in citations_by_file.items():
                    if filename.endswith('.pdf'):
                        st.markdown(f"**📄 {filename}**")
                        
                        # Create a button to open the document viewer with all citations
                        viewer_url = create_document_viewer_url(filename, file_citations)
                        st.markdown(f'<a href="{viewer_url}" target="_blank" style="text-decoration: none;"><button style="background: #2196f3; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; margin-bottom: 10px;">🔍 Open Document Viewer</button></a>', unsafe_allow_html=True)
                        
                        # List the citations for this file
                        for citation in file_citations:
                            col1, col2 = st.columns([4, 1])
                            with col1:
                                st.write(f"   • **[Source {citation['source_num']}]** Page {citation['page']}")
                            with col2:
                                # Button to open viewer focused on this specific citation
                                focused_url = create_document_viewer_url(filename, file_citations, citation['source_num'])
                                st.markdown(f'<a href="{focused_url}" target="_blank" style="text-decoration: none;"><button style="background: #ff9800; color: white; border: none; padding: 4px 8px; border-radius: 3px; cursor: pointer; font-size: 12px;">📍 Go to Source</button></a>', unsafe_allow_html=True)
                        
                        st.markdown("---")
                    else:
                        # Non-PDF files
                        for citation in file_citations:
                            st.write(f"• **[Source {citation['source_num']}]** {citation['filename']}, p. {citation['page']}")
        
        # Add assistant message to chat history with enhanced citations
        st.session_state.messages.append({
            "role": "assistant", 
            "content": result["response_text"],
            "citations": result["citations"],
            "enhanced_citations": result.get("enhanced_citations", result["citations"])  # Store enhanced citations
        })

# Document Navigation Instructions
if st.session_state.messages:
    # Check if there are any PDF citations
    has_pdf_citations = False
    for message in st.session_state.messages:
        if message.get("role") == "assistant" and message.get("citations"):
            for citation in message["citations"]:
                if citation.get("filename", "").endswith(".pdf"):
                    has_pdf_citations = True
                    break
    
    if has_pdf_citations:
        st.markdown("---")

# # Show chat stats in sidebar
# with st.sidebar:
#     if st.session_state.messages:
#         st.markdown("---")
#         st.subheader("📊 Chat Stats")
#         user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
#         assistant_messages = len([m for m in st.session_state.messages if m["role"] == "assistant"])
#         st.write(f"• **Questions asked:** {user_messages}")
#         st.write(f"• **Responses given:** {assistant_messages}")
        
#         # Show context option for last response
#         if assistant_messages > 0:
#             if st.checkbox("Show last context used"):
#                 if 'last_context' in st.session_state:
#                     st.text_area("Last Context", st.session_state.last_context, height=200, key="context_display", disabled=True)
