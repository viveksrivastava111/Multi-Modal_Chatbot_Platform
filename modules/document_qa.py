"""
Document Q&A (RAG) module.

Pipeline: upload -> split into chunks -> embed with FastEmbed (local,
no API key needed) -> store in a DocArrayInMemorySearch vector store
-> retrieve top-k relevant chunks -> answer with the selected LLM,
grounded only in the retrieved context, with multi-turn memory so
follow-up questions ("what about the second point?") still work.
"""
import tempfile
import os

import streamlit as st
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.messages import SystemMessage, HumanMessage

from utils import memory_manager as mem
from utils.llm_manager import get_llm, get_embeddings
import config

MEM_KEY = "history_doc_qa"

SYSTEM_TEMPLATE = (
    "You are a document Q&A assistant. Answer the user's question using ONLY "
    "the context below. If the answer isn't in the context, say you don't "
    "know rather than guessing.\n\nContext:\n{context}"
)


def _load_document(uploaded_file) -> list:
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
    finally:
        os.unlink(tmp_path)
    return docs


@st.cache_resource(show_spinner=False)
def _build_vectorstore(file_bytes_hash: str, _docs, _embeddings):
    """Cached by a hash of the file content so re-uploading the same
    file doesn't re-embed it every rerun."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE, chunk_overlap=config.CHUNK_OVERLAP
    )
    chunks = splitter.split_documents(_docs)
    store = DocArrayInMemorySearch.from_documents(chunks, _embeddings)
    return store


def render(provider: str, model_name: str):
    st.subheader("📄 Document Q&A (RAG)")
    st.caption("Upload a PDF, DOCX, or TXT file and ask questions grounded in its content.")

    mem.init_memory(MEM_KEY)

    uploaded_file = st.file_uploader("Upload a document", type=["pdf", "docx", "txt"])

    if uploaded_file is None:
        st.info("Upload a document to get started.")
        return

    file_hash = str(hash(uploaded_file.getvalue()))

    with st.spinner("Reading and embedding document..."):
        docs = _load_document(uploaded_file)
        embeddings = get_embeddings()
        vectorstore = _build_vectorstore(file_hash, docs, embeddings)

    st.success(f"Loaded **{uploaded_file.name}** — {len(docs)} page(s)/section(s) indexed.")

    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("🗑️ Clear chat", use_container_width=True):
            mem.clear_memory(MEM_KEY)
            st.rerun()

    mem.render_chat_history(MEM_KEY)

    question = st.chat_input("Ask something about the document...")
    if not question:
        return

    mem.add_user_message(MEM_KEY, question)
    with st.chat_message("user"):
        st.markdown(question)

    try:
        retriever = vectorstore.as_retriever(search_kwargs={"k": config.RETRIEVER_TOP_K})
        relevant_docs = retriever.invoke(question)
        context = "\n\n---\n\n".join(d.page_content for d in relevant_docs)

        llm = get_llm(provider, model_name)
        messages = [
            SystemMessage(content=SYSTEM_TEMPLATE.format(context=context)),
            *mem.get_history(MEM_KEY)[-6:],  # last few turns for follow-ups
        ]

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""
            for chunk in llm.stream(messages):
                full_response += chunk.content or ""
                placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)

            with st.expander("📎 Sources used"):
                for i, d in enumerate(relevant_docs, 1):
                    page = d.metadata.get("page", "N/A")
                    st.markdown(f"**Chunk {i}** (page {page})")
                    st.text(d.page_content[:400] + ("..." if len(d.page_content) > 400 else ""))

        mem.add_ai_message(MEM_KEY, full_response)

    except Exception as e:
        st.error(f"Error: {e}")
