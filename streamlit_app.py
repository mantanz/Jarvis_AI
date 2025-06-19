import streamlit as st
from processing import load_documents, split_documents, add_to_chroma, clear_database
from query_data import query_rag

st.set_page_config(page_title="RAG Pipeline App", page_icon="📚")

# Custom CSS for tooltips
st.markdown("""
<style>
    .citation-tooltip {
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
    }

    .citation-tooltip:hover {
        background-color: #cce6ff;
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

    /* Enhanced visibility */
    .citation-tooltip {
        transition: all 0.2s ease;
    }

    .citation-tooltip:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0,102,204,0.2);
    }
</style>
""", unsafe_allow_html=True)

st.title("RAG Pipeline")

# Add info about tooltips
st.info("💡 **Tip:** Hover over citation links [Source X] in responses to see detailed source information!")

def format_response_with_streamlit_tooltips(response_text: str, citations: list) -> str:
    """
    Format response text with Streamlit-compatible tooltip HTML.
    """
    import re
    
    formatted_response = response_text
    
    # Create a mapping of citation numbers to tooltip data
    citation_tooltips = {}
    for citation in citations:
        citation_tooltips[citation["source_num"]] = citation["tooltip_text"]
    
    # Replace citations with tooltip-enabled spans
    for source_num, tooltip_text in citation_tooltips.items():
        # Escape quotes in tooltip text for HTML attributes
        escaped_tooltip = tooltip_text.replace('"', '&quot;').replace("'", "&#39;")
        
        # Create tooltip HTML with proper structure for Streamlit
        tooltip_html = f'''
        <span class="tooltip citation-tooltip">
            [Source {source_num}]
            <span class="tooltiptext">{escaped_tooltip}</span>
        </span>'''
        
        # Replace [Source X] with tooltip-enabled span
        formatted_response = re.sub(
            f'\\[Source {source_num}\\]',
            tooltip_html,
            formatted_response
        )
    
    return formatted_response

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

# Main chat interface


# Display chat messages
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                # Display response with tooltips if citations exist
                if message.get("citations"):
                    response_with_tooltips = format_response_with_streamlit_tooltips(
                        message["content"], 
                        message["citations"]
                    )
                    st.markdown(response_with_tooltips, unsafe_allow_html=True)
                else:
                    st.write(message["content"])
                
                # Show expandable sources section as backup
                if message.get("citations"):
                    with st.expander(f"📚 Sources ({len(message['citations'])} cited)", expanded=False):
                        for citation in message["citations"]:
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
        
        # Display the response with tooltips
        if result["citations"]:
            response_with_tooltips = format_response_with_streamlit_tooltips(
                result["response_text"], 
                result["citations"]
            )
            st.markdown(response_with_tooltips, unsafe_allow_html=True)
        else:
            st.write(result["response_text"])
        
        # Show expandable sources section
        if result["citations"]:
            with st.expander(f"📚 Sources ({len(result['citations'])} cited)", expanded=False):
                for citation in result["citations"]:
                    st.write(f"• **[Source {citation['source_num']}]** {citation['filename']}, p. {citation['page']}")
        
        # Add assistant message to chat history
        st.session_state.messages.append({
            "role": "assistant", 
            "content": result["response_text"],
            "citations": result["citations"]
        })

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
