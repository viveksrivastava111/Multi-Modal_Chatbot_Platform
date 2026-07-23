"""
Multi-Modal Chatbot Platform
=============================
A single Streamlit app hosting six AI modules powered by LangChain,
switchable between OpenAI and local Ollama models:

  1. General Chat            - context-aware conversation with memory
  2. Document Q&A (RAG)       - LangChain + FastEmbed + DocArray retrieval
  3. SQL Query Assistant      - natural language -> SQL over SQLite
  4. Web Search Assistant     - live DuckDuckGo search + synthesis
  5. Image Analysis           - multi-modal vision Q&A
  6. Text Summarizer          - bullet/paragraph/executive summaries

Run with:  streamlit run app.py
"""
import streamlit as st

import config
from modules import general_chat, document_qa, sql_assistant, web_search, image_analysis, summarizer

st.set_page_config(page_title=config.APP_TITLE, page_icon=config.APP_ICON, layout="wide")


def sidebar_controls():
    st.sidebar.title(f"{config.APP_ICON} {config.APP_TITLE}")
    st.sidebar.caption("LangChain • FastEmbed • DocArray • Streamlit")

    provider = st.sidebar.selectbox(
        "LLM Provider", ["OpenAI", "Ollama"],
        index=["OpenAI", "Ollama"].index(config.DEFAULT_PROVIDER),
        help="OpenAI needs an API key in .env. Ollama runs fully locally and free.",
    )

    model_list = config.OPENAI_MODELS if provider == "OpenAI" else config.OLLAMA_MODELS
    model_name = st.sidebar.selectbox("Model", model_list)

    if provider == "OpenAI" and not config.OPENAI_API_KEY:
        st.sidebar.warning("No OPENAI_API_KEY set — add one to your .env file, or switch to Ollama.")

    st.sidebar.divider()
    module = st.sidebar.radio("Choose a module", config.MODULES)
    st.sidebar.divider()
    st.sidebar.markdown(
        "**About**\n\n"
        "This platform demonstrates RAG, text-to-SQL, live web search, "
        "vision, and summarization — all behind one memory-aware chat "
        "interface, switchable between cloud (OpenAI) and local (Ollama) LLMs."
    )
    return provider, model_name, module


def main():
    provider, model_name, module = sidebar_controls()

    if module == "💬 General Chat":
        general_chat.render(provider, model_name)
    elif module == "📄 Document Q&A (RAG)":
        document_qa.render(provider, model_name)
    elif module == "🗃️ SQL Query Assistant":
        sql_assistant.render(provider, model_name)
    elif module == "🌐 Web Search Assistant":
        web_search.render(provider, model_name)
    elif module == "🖼️ Image Analysis":
        image_analysis.render(provider, model_name)
    elif module == "📝 Text Summarizer":
        summarizer.render(provider, model_name)


if __name__ == "__main__":
    main()
