"""
memory_manager.py
------------------
Lightweight wrapper around Streamlit's session_state so every module
gets its own isolated chat history / memory, keyed by module name.
This gives context-aware, multi-turn conversations without modules
stepping on each other's history.
"""
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage


def init_memory(key: str):
    """Ensure a message list exists in session_state for this module."""
    if key not in st.session_state:
        st.session_state[key] = []


def get_history(key: str):
    return st.session_state.get(key, [])


def add_user_message(key: str, content: str):
    init_memory(key)
    st.session_state[key].append(HumanMessage(content=content))


def add_ai_message(key: str, content: str):
    init_memory(key)
    st.session_state[key].append(AIMessage(content=content))


def clear_memory(key: str):
    st.session_state[key] = []


def render_chat_history(key: str):
    """Render the stored history as Streamlit chat bubbles."""
    for msg in get_history(key):
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        with st.chat_message(role):
            st.markdown(msg.content)
