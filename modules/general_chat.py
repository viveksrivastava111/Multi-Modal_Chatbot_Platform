"""
General Chat module — a plain context-aware conversational assistant.
Demonstrates multi-turn memory: every previous message in the session
is replayed to the model so it remembers what was said earlier.
"""
import streamlit as st
from langchain_core.messages import SystemMessage

from utils import memory_manager as mem
from utils.llm_manager import get_llm

MEM_KEY = "history_general_chat"

SYSTEM_PROMPT = (
    "You are a helpful, friendly general-purpose assistant. "
    "Keep answers concise unless the user asks for detail."
)


def render(provider: str, model_name: str):
    st.subheader("💬 General Chat")
    st.caption("A context-aware assistant that remembers the whole conversation.")

    mem.init_memory(MEM_KEY)

    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            mem.clear_memory(MEM_KEY)
            st.rerun()

    mem.render_chat_history(MEM_KEY)

    user_input = st.chat_input("Type a message...")
    if not user_input:
        return

    mem.add_user_message(MEM_KEY, user_input)
    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        llm = get_llm(provider, model_name)
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + mem.get_history(MEM_KEY)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""
            for chunk in llm.stream(messages):
                full_response += chunk.content or ""
                placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)

        mem.add_ai_message(MEM_KEY, full_response)

    except Exception as e:
        st.error(f"Error: {e}")
