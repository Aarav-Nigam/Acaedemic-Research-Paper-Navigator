import streamlit as st
from backend.qa_pipeline import load_retriever, build_qa_chain

def render_chat_ui():
    st.title("💬 Ask Questions About Your Paper")

    paper_id = st.text_input("Enter paper ID used in upload:", key="chat_paper_id")
    if not paper_id:
        st.warning("Please enter a paper ID.")
        return

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    retriever = load_retriever(paper_id)
    qa_chain = build_qa_chain(retriever)

    query = st.text_input("Ask a question:", key="user_question")

    if st.button("Ask") and query:
        with st.spinner("Thinking..."):
            result = qa_chain.invoke({"question": query, "chat_history": st.session_state.chat_history})
            st.session_state.chat_history.append((query, result["answer"]))
            st.success(result)

    st.markdown("---")
    st.subheader("📝 Conversation History")
    for i, (q, a) in enumerate(st.session_state.chat_history):
        st.markdown(f"**Q{i+1}:** {q}")
        st.markdown(f"> {a}")
