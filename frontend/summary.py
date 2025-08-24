import streamlit as st
from backend.summarizer import summarize_text
from utils.chunking import extract_full_text
from utils.session_manager import session_manager
import os
import re

def parse_summary_response(response):
    """Parse summary response to separate thinking and final summary"""
    if not response:
        return {"thinking": "", "summary": ""}
    
    # Extract thinking content from <think> tags
    think_match = re.search(r'<think>(.*?)</think>', response, flags=re.DOTALL | re.IGNORECASE)
    thinking_content = think_match.group(1).strip() if think_match else ""
    
    # Extract the summary part (everything outside <think> tags)
    summary_content = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL | re.IGNORECASE)
    summary_content = summary_content.strip()
    
    # If no summary content found outside think tags, use the original response
    if not summary_content and not thinking_content:
        summary_content = response
    
    return {
        "thinking": thinking_content,
        "summary": summary_content
    }

def render_summary_ui():
    st.title("📄 Paper Summary & Key Points")
    
    # Get available PDFs for current session
    current_pdfs = session_manager.get_session_pdfs(st.session_state.user_session_id)
    
    if not current_pdfs:
        st.info("📭 No PDFs in current session. Please upload PDFs first.")
        return
    
    # PDF Selection Section
    st.subheader("📚 Select PDFs for Summary")
    
    # Initialize selected PDFs in session state for summary
    if "selected_summary_pdfs" not in st.session_state:
        st.session_state.selected_summary_pdfs = []
    
    # PDF selection with radio buttons for single selection or checkboxes for multiple
    summary_mode = st.radio(
        "Summary Mode:",
        ["📄 Individual Summary", "📚 Combined Summary"],
        help="Choose to summarize one PDF at a time or combine multiple PDFs"
    )
    
    selected_pdfs = []
    
    if summary_mode == "📄 Individual Summary":
        # Single PDF selection
        selected_pdf = st.selectbox(
            "Choose a PDF to summarize:",
            [""] + current_pdfs,
            format_func=lambda x: f"📄 {x}" if x else "Select a PDF..."
        )
        if selected_pdf:
            selected_pdfs = [selected_pdf]
    else:
        # Multiple PDF selection
        st.write("Select multiple PDFs to create a combined summary:")
        for pdf_name in current_pdfs:
            if st.checkbox(f"📄 {pdf_name}", key=f"summary_select_{pdf_name}"):
                selected_pdfs.append(pdf_name)
    
    st.session_state.selected_summary_pdfs = selected_pdfs
    
    if not selected_pdfs:
        st.warning("Please select at least one PDF to summarize.")
        return
    
    # Show selected PDFs summary
    if len(selected_pdfs) == 1:
        st.info(f"📊 Selected PDF: {selected_pdfs[0]}")
    else:
        st.info(f"📊 Selected {len(selected_pdfs)} PDFs: {', '.join(selected_pdfs)}")
    
    # Summary options
    st.markdown("---")
    st.subheader("⚙️ Summary Options")
    
    col1, col2 = st.columns(2)
    with col1:
        summary_length = st.selectbox(
            "Summary Length:",
            ["Short", "Medium", "Detailed"],
            index=1,
            help="Choose the desired length of the summary"
        )
    
    with col2:
        summary_focus = st.selectbox(
            "Summary Focus:",
            ["General Overview", "Key Findings", "Methodology", "Results & Conclusions"],
            help="Choose what aspect to focus on in the summary"
        )
    
    # Include key points option
    include_key_points = st.checkbox(
        "📋 Include Key Points & Takeaways",
        value=True,
        help="Extract bullet-pointed key insights"
    )
    
    # Generate Summary Button
    st.markdown("---")
    if st.button("🧠 Generate Summary", type="primary", use_container_width=True):
        if selected_pdfs:
            with st.spinner("📖 Reading and analyzing the selected PDF(s)..."):
                try:
                    user_dir = os.path.join("data", "temp_sessions", st.session_state.user_session_id, "pdfs")
                    
                    # Extract text from selected PDFs
                    combined_text = ""
                    pdf_info = []
                    
                    for pdf_name in selected_pdfs:
                        pdf_path = os.path.join(user_dir, pdf_name)
                        if os.path.exists(pdf_path):
                            text = extract_full_text(pdf_path)
                            combined_text += f"\n\n=== {pdf_name} ===\n{text}"
                            pdf_info.append({
                                "name": pdf_name,
                                "word_count": len(text.split()),
                                "char_count": len(text)
                            })
                        else:
                            st.error(f"❌ PDF not found: {pdf_name}")
                            continue
                    
                    if not combined_text.strip():
                        st.error("❌ No text could be extracted from the selected PDF(s)")
                        return
                    
                    # Generate summary with options
                    summary_prompt = f"""
                    Please provide a {summary_length.lower()} summary focusing on {summary_focus.lower()} 
                    for the following document(s). {'Also include key points and takeaways.' if include_key_points else ''}
                    """
                    
                    summary = summarize_text(combined_text, summary_prompt)
                    
                    # Parse the response to separate thinking and summary
                    parsed_response = parse_summary_response(summary)
                    
                    # Display PDF information
                    st.markdown("### 📊 **Document Information**")
                    info_cols = st.columns(len(pdf_info)) if len(pdf_info) <= 3 else st.columns(3)
                    
                    for i, info in enumerate(pdf_info):
                        with info_cols[i % len(info_cols)]:
                            st.metric(
                                label=f"📄 {info['name'][:20]}...",
                                value=f"{info['word_count']:,} words",
                                delta=f"{info['char_count']:,} chars"
                            )
                    
                    # Display thinking process if available
                    if parsed_response["thinking"]:
                        st.markdown("### 🧠 **Analysis Process**")
                        with st.container():
                            st.markdown(
                                f"""
                                <div style='background-color: rgba(31,119,180,0.1); color: inherit; padding: 15px; border-radius: 10px; border-left: 4px solid #1f77b4; margin: 10px 0;'>
                                    <strong>💭 Processing Steps:</strong><br>
                                    {parsed_response["thinking"].replace(chr(10), '<br>')}
                                </div>
                                """, 
                                unsafe_allow_html=True
                            )
                    
                    # Display the summary
                    st.markdown("### 📝 **Summary**")
                    clean_summary = parsed_response["summary"] if parsed_response["summary"] else summary
                    
                    # Create a nice container for the summary with proper markdown rendering
                    with st.container():
                        st.markdown(
                            f"""
                            <div style='background-color: rgba(40,167,69,0.1); color: inherit; padding: 20px; border-radius: 10px; border-left: 4px solid #28a745; margin: 10px 0;'>
                                {clean_summary}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    
                    # Store summary in session state for history
                    if "summary_history" not in st.session_state:
                        st.session_state.summary_history = []
                    
                    summary_entry = {
                        "pdfs": selected_pdfs.copy(),
                        "mode": summary_mode,
                        "length": summary_length,
                        "focus": summary_focus,
                        "summary": clean_summary,
                        "timestamp": st.timestamp if hasattr(st, 'timestamp') else "Recent"
                    }
                    st.session_state.summary_history.append(summary_entry)
                    
                    # Download summary option
                    st.markdown("---")
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.download_button(
                            label="📥 Download Summary",
                            data=clean_summary,
                            file_name=f"summary_{'_'.join(selected_pdfs)}.txt",
                            mime="text/plain",
                            help="Download the summary as a text file"
                        )
                    
                    with col2:
                        if st.button("📋 Copy to Clipboard"):
                            # Note: Actual clipboard functionality would need additional setup
                            st.info("💡 Use Ctrl+C to copy the summary text above")
                    
                except Exception as e:
                    st.error(f"❌ Error generating summary: {str(e)}")
                    st.exception(e)  # For debugging
    
    # Summary History Section
    if hasattr(st.session_state, 'summary_history') and st.session_state.summary_history:
        st.markdown("---")
        st.subheader("📚 Summary History")
        
        # Display recent summaries without nested expanders
        for i, entry in enumerate(reversed(st.session_state.summary_history[-5:])):  # Show last 5
            history_num = len(st.session_state.summary_history) - i
            pdfs_text = ", ".join(entry["pdfs"])
            
            # Create a container for each summary entry
            st.markdown(f"#### 📄 Summary #{history_num}")
            st.markdown(f"**Files:** {pdfs_text}")
            
            # Summary details in columns
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**📏 Length:** {entry['length']}")
                st.markdown(f"**🎯 Focus:** {entry['focus']}")
            with col2:
                st.markdown(f"**📊 Mode:** {entry['mode']}")
            
            # Summary content with toggle
            summary_key = f"show_full_summary_{history_num}"
            if summary_key not in st.session_state:
                st.session_state[summary_key] = False
            
            # Show preview or full summary
            if len(entry['summary']) > 300:
                if not st.session_state[summary_key]:
                    st.markdown("**📝 Summary Preview:**")
                    preview_text = entry['summary'][:300] + "..."
                    with st.container():
                        st.markdown(
                            f"""
                            <div style='background-color: rgba(40, 167, 69, 0.1); color: inherit; padding: 15px; border-radius: 10px; border-left: 4px solid #28a745; margin: 10px 0;'>
                                {preview_text}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    
                    if st.button(f"📖 Show Full Summary", key=f"expand_{history_num}"):
                        st.session_state[summary_key] = True
                        st.rerun()
                else:
                    st.markdown("**📝 Full Summary:**")
                    with st.container():
                        st.markdown(
                            f"""
                            <div style='background-color: rgba(40, 167, 69, 0.1); color: inherit; padding: 15px; border-radius: 10px; border-left: 4px solid #28a745; margin: 10px 0;'>
                                {entry['summary']}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    
                    if st.button(f"📄 Show Preview Only", key=f"collapse_{history_num}"):
                        st.session_state[summary_key] = False
                        st.rerun()
            else:
                st.markdown("**📝 Summary:**")
                with st.container():
                    st.markdown(
                        f"""
                        <div style='background-color: rgba(40, 167, 69, 0.1); color: inherit; padding: 15px; border-radius: 10px; border-left: 4px solid #28a745; margin: 10px 0;'>
                            {entry['summary']}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            
            st.markdown("---")  # Separator between entries
    
    # Clear History Button
    if hasattr(st.session_state, 'summary_history') and st.session_state.summary_history:
        st.markdown("---")
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🗑️ Clear Summary History", type="secondary"):
                st.session_state.confirm_clear_summary = True
        
        with col2:
            if st.button("📊 Summary Stats", type="secondary"):
                total_summaries = len(st.session_state.summary_history)
                unique_pdfs = set()
                for entry in st.session_state.summary_history:
                    unique_pdfs.update(entry['pdfs'])
                
                st.info(f"""
                **Summary Statistics:**
                - Total Summaries Generated: {total_summaries}
                - Unique PDFs Summarized: {len(unique_pdfs)}
                - Available PDFs: {len(current_pdfs)}
                """)
        
        # Confirmation dialog for clearing history
        if st.session_state.get("confirm_clear_summary", False):
            st.warning("⚠️ Are you sure you want to clear the summary history?")
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("✅ Yes, Clear History", type="primary"):
                    st.session_state.summary_history = []
                    st.session_state.confirm_clear_summary = False
                    st.success("✅ Summary history cleared!")
                    st.rerun()
            
            with col2:
                if st.button("❌ Cancel"):
                    st.session_state.confirm_clear_summary = False
                    st.rerun()


# Updated backend/summarizer.py
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

def summarize_text(text, custom_prompt=""):
    """Generate summary using Groq API with optional custom prompt"""
    try:
        llm = ChatGroq(
            model="qwen/qwen/qwen3-32b",
            groq_api_key=os.getenv("GROQ_API"),
            temperature=0.3
        )
        
        base_prompt = f"""
        {custom_prompt if custom_prompt else 'Please provide a comprehensive summary of the following document(s).'}
        
        Focus on:
        1. Main topics and themes
        2. Key findings and insights
        3. Important conclusions
        4. Significant data or results
        
        Document(s) to summarize:
        {text[:8000]}  # Limit text to avoid token limits
        """
        
        response = llm.invoke(base_prompt)
        return response.content
        
    except Exception as e:
        return f"Error generating summary: {str(e)}"