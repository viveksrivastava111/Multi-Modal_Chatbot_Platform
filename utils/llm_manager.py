"""
llm_manager.py
--------------
Single place responsible for instantiating the correct chat model
(OpenAI or Ollama) so every module can just call get_llm() and not
worry about provider-specific setup.
"""
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_community.embeddings import FastEmbedEmbeddings

import config


def get_llm(provider: str, model_name: str, temperature: float = 0.3, streaming: bool = True):
    """
    Return a LangChain chat model instance for the requested provider.

    provider: "OpenAI" or "Ollama"
    model_name: e.g. "gpt-4o-mini" or "llama3.1"
    """
    if provider == "OpenAI":
        if not config.OPENAI_API_KEY:
            raise ValueError(
                "No OPENAI_API_KEY found. Add it to your .env file, "
                "or switch the provider to 'Ollama' in the sidebar."
            )
        return ChatOpenAI(
            model=model_name,
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL,
            temperature=temperature,
            streaming=streaming,
        )

    if provider == "Ollama":
        return ChatOllama(
            model=model_name,
            base_url=config.OLLAMA_HOST,
            temperature=temperature,
        )

    raise ValueError(f"Unknown provider: {provider}")


def get_embeddings():
    """
    FastEmbed runs fully locally (ONNX runtime under the hood) so document
    embedding never requires an API key or internet call at inference time.
    """
    return FastEmbedEmbeddings(model_name=config.EMBEDDING_MODEL)
