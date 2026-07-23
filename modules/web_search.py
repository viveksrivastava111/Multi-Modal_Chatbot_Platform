"""
Web Search Assistant module.

Uses DuckDuckGo search (no API key required) to fetch fresh results,
then asks the LLM to synthesize a grounded, cited answer — useful for
questions about recent events beyond the model's training data.
"""
import streamlit as st
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.messages import SystemMessage, HumanMessage

from utils.llm_manager import get_llm

SYSTEM_PROMPT = (
    "You are a research assistant. You are given fresh web search results. "
    "Synthesize a clear, well-organized answer to the user's question using "
    "only the information in the results. Mention source titles when relevant. "
    "If the results don't answer the question, say so."
)


def render(provider: str, model_name: str):
    st.subheader("🌐 Web Search Assistant")
    st.caption("Searches the live web (DuckDuckGo) and summarizes the answer for you.")

    query = st.text_input("What do you want to know?", placeholder="e.g. Latest developments in small language models")
    search_btn = st.button("Search", type="primary")

    if not (search_btn and query):
        return

    try:
        with st.spinner("Searching the web..."):
            search_tool = DuckDuckGoSearchResults(output_format="list", num_results=6)
            results = search_tool.invoke(query)

        if not results:
            st.warning("No results found. Try rephrasing your query.")
            return

        with st.expander(f"🔎 {len(results)} raw results used"):
            for r in results:
                st.markdown(f"**{r.get('title', 'Untitled')}**")
                st.caption(r.get("link", ""))
                st.write(r.get("snippet", ""))
                st.divider()

        context = "\n\n".join(
            f"Title: {r.get('title')}\nSnippet: {r.get('snippet')}\nLink: {r.get('link')}"
            for r in results
        )

        llm = get_llm(provider, model_name)
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Question: {query}\n\nSearch results:\n{context}"),
        ]

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""
            for chunk in llm.stream(messages):
                full_response += chunk.content or ""
                placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)

    except Exception as e:
        st.error(f"Error: {e}")
