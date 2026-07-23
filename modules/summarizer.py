"""
Text Summarizer module — paste text or upload a file and get a
summary at the length/style of your choice (bullet points, one
paragraph, or executive summary).
"""
import tempfile
import os

import streamlit as st
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_core.messages import SystemMessage, HumanMessage

from utils.llm_manager import get_llm

STYLE_PROMPTS = {
    "Bullet points": "Summarize the text as a concise list of bullet points capturing the key ideas.",
    "One paragraph": "Summarize the text in a single, well-written paragraph.",
    "Executive summary": (
        "Write a short executive summary with a one-line takeaway, followed by "
        "3-5 key points, suitable for a busy stakeholder."
    ),
}


def _load_text_from_file(uploaded_file) -> str:
    suffix = os.path.splitext(uploaded_file.name)[1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getbuffer())
        tmp_path = tmp.name
    try:
        if suffix == ".pdf":
            loader = PyPDFLoader(tmp_path)
        elif suffix == ".docx":
            loader = Docx2txtLoader(tmp_path)
        else:
            loader = TextLoader(tmp_path, encoding="utf-8")
        docs = loader.load()
        return "\n\n".join(d.page_content for d in docs)
    finally:
        os.unlink(tmp_path)


def render(provider: str, model_name: str):
    st.subheader("📝 Text Summarizer")
    st.caption("Paste text or upload a document, choose a style, and get a summary.")

    tab1, tab2 = st.tabs(["Paste text", "Upload file"])
    source_text = ""

    with tab1:
        pasted = st.text_area("Paste text to summarize", height=200)
        if pasted:
            source_text = pasted

    with tab2:
        uploaded_file = st.file_uploader("Upload a PDF, DOCX, or TXT file", type=["pdf", "docx", "txt"])
        if uploaded_file:
            source_text = _load_text_from_file(uploaded_file)
            st.success(f"Loaded {len(source_text)} characters from {uploaded_file.name}.")

    style = st.selectbox("Summary style", list(STYLE_PROMPTS.keys()))
    summarize_btn = st.button("Summarize", type="primary")

    if not (summarize_btn and source_text.strip()):
        if summarize_btn:
            st.warning("Please paste some text or upload a file first.")
        return

    try:
        llm = get_llm(provider, model_name, temperature=0.3)

        # Simple map-reduce for long text to stay within context limits
        max_chars = 12000
        if len(source_text) > max_chars:
            chunks = [source_text[i:i + max_chars] for i in range(0, len(source_text), max_chars)]
            partial_summaries = []
            with st.spinner(f"Summarizing {len(chunks)} chunks..."):
                for c in chunks:
                    msg = [
                        SystemMessage(content="Summarize this chunk concisely, preserving key facts."),
                        HumanMessage(content=c),
                    ]
                    partial_summaries.append(llm.invoke(msg).content)
            source_text = "\n\n".join(partial_summaries)

        final_messages = [
            SystemMessage(content=STYLE_PROMPTS[style]),
            HumanMessage(content=source_text),
        ]

        with st.spinner("Generating final summary..."):
            summary = llm.invoke(final_messages).content

        st.markdown("**Summary:**")
        st.write(summary)

    except Exception as e:
        st.error(f"Error: {e}")
