"""
Image Analysis module — the "multi-modal" part of the platform.

Sends an uploaded image plus a text prompt to a vision-capable model
(GPT-4o / GPT-4o-mini for OpenAI, or a vision Ollama model like
"llava" if the user has one pulled locally) and returns a description
or answer to a specific question about the image.
"""
import base64

import streamlit as st
from langchain_core.messages import HumanMessage

from utils.llm_manager import get_llm

DEFAULT_PROMPT = "Describe this image in detail."


def _encode_image(uploaded_file) -> str:
    return base64.b64encode(uploaded_file.getvalue()).decode("utf-8")


def render(provider: str, model_name: str):
    st.subheader("🖼️ Image Analysis")
    st.caption("Upload an image and ask a question about it (uses a vision-capable model).")

    if provider == "Ollama":
        st.info(
            "For Ollama, use a vision model such as **llava** (pull it with "
            "`ollama pull llava`) and select it from the sidebar model list."
        )

    uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "webp"])
    if not uploaded_image:
        return

    st.image(uploaded_image, caption=uploaded_image.name, use_container_width=True)

    prompt = st.text_input("What do you want to know about this image?", value=DEFAULT_PROMPT)
    analyze_btn = st.button("Analyze", type="primary")

    if not analyze_btn:
        return

    try:
        b64_image = _encode_image(uploaded_image)
        mime = uploaded_image.type or "image/png"

        llm = get_llm(provider, model_name, temperature=0.2)

        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64_image}"}},
            ]
        )

        with st.spinner("Analyzing image..."):
            response = llm.invoke([message])

        st.markdown("**Result:**")
        st.write(response.content)

    except Exception as e:
        st.error(
            f"Error: {e}\n\nNote: not every model supports images — make sure you've "
            "selected a vision-capable model (e.g. gpt-4o, gpt-4o-mini, or llava)."
        )
