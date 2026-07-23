# 🧠 Multi-Modal Chatbot Platform

A single Streamlit application hosting **six AI-powered modules** behind one
memory-aware chat interface, built with **LangChain, FastEmbed, and DocArray**,
and switchable between **OpenAI** (cloud) and **Ollama** (local, free) LLMs.

| Module | What it does |
|---|---|
| 💬 **General Chat** | Context-aware conversation with per-session memory |
| 📄 **Document Q&A (RAG)** | Upload a PDF/DOCX/TXT → chunk → embed with **FastEmbed** → store in a **DocArray** vector store → answer questions grounded in the document, with cited source chunks |
| 🗃️ **SQL Query Assistant** | Ask questions in plain English → LLM writes SQL against the schema → query runs on SQLite → LLM explains the result in plain English |
| 🌐 **Web Search Assistant** | Live DuckDuckGo search → LLM synthesizes a grounded, up-to-date answer |
| 🖼️ **Image Analysis** | Multi-modal vision Q&A on an uploaded image (GPT-4o / GPT-4o-mini, or `llava` via Ollama) |
| 📝 **Text Summarizer** | Paste text or upload a file → choose bullet points / paragraph / executive-summary style, with automatic map-reduce chunking for long documents |

---

## ✨ Highlights (for resume / portfolio)

- **RAG pipeline** built with LangChain, FastEmbed embeddings, and a DocArray in-memory vector store — no external vector DB service required.
- **Dual LLM backend**: works with OpenAI's API *or* fully local, free inference via Ollama — one toggle in the sidebar.
- **Memory management** per module using LangChain message objects, so multi-turn conversations stay context-aware.
- **Text-to-SQL** module that inspects a live database schema, generates SQL, executes it safely, and explains results in natural language.
- **Modular architecture** — each capability is an isolated Python module (`modules/`) behind a shared `utils/llm_manager.py`, making it trivial to add a 7th module later.

---

## 🗂️ Project structure

```
multimodal-chatbot-platform/
├── app.py                     # Streamlit entry point / sidebar / routing
├── config.py                  # Central settings (models, paths, prompts)
├── requirements.txt
├── .env.example                # Copy to .env and add your OpenAI key (optional)
├── modules/
│   ├── general_chat.py
│   ├── document_qa.py         # RAG: FastEmbed + DocArray
│   ├── sql_assistant.py       # Text-to-SQL
│   ├── web_search.py          # DuckDuckGo + synthesis
│   ├── image_analysis.py      # Vision Q&A
│   └── summarizer.py
├── utils/
│   ├── llm_manager.py         # OpenAI/Ollama switch + FastEmbed embeddings
│   └── memory_manager.py      # Per-module chat memory (Streamlit session_state)
├── scripts/
│   └── build_sample_db.py     # Generates the demo SQLite database
└── data/
    └── sample.db               # Demo e-commerce database (customers/products/orders)
```

---

## 🚀 Getting started

### 1. Clone and install
```bash
git clone <your-repo-url>
cd multimodal-chatbot-platform
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure a model backend
You only need **one** of these:

**Option A — OpenAI (cloud)**
```bash
cp .env.example .env
# edit .env and paste your OPENAI_API_KEY
```

**Option B — Ollama (free, fully local)**
```bash
# install from https://ollama.com, then:
ollama pull llama3.1
ollama pull llava     # optional, only needed for the Image Analysis module
```
No `.env` changes needed — just pick "Ollama" in the app's sidebar.

### 3. (Re)generate the sample database (optional — one is already included)
```bash
python scripts/build_sample_db.py
```

### 4. Run the app
```bash
streamlit run app.py
```
Open the URL Streamlit prints (usually `http://localhost:8501`).

---

## 🧩 How the RAG pipeline works (Document Q&A)

1. **Load** — `PyPDFLoader` / `Docx2txtLoader` / `TextLoader` reads the uploaded file.
2. **Split** — `RecursiveCharacterTextSplitter` breaks it into ~1000-character overlapping chunks.
3. **Embed** — `FastEmbedEmbeddings` (ONNX runtime, runs locally, no API key) turns each chunk into a vector.
4. **Store & retrieve** — chunks are indexed in a `DocArrayInMemorySearch` vector store; the top-k most similar chunks to the question are retrieved.
5. **Answer** — the retrieved chunks are injected into the system prompt, and the selected LLM answers *only* from that context, with the source chunks shown in an expander for transparency.

## 🧩 How the SQL assistant works

1. The app introspects the SQLite schema (`PRAGMA table_info`) and shows it to the LLM.
2. The LLM is asked to return a single raw SQL query for the user's question.
3. The query runs via `pandas.read_sql_query` against the database (sandboxed to that one file).
4. The result is shown as a table, and the LLM is asked again to explain the numbers in plain English.

---

## 🔧 Extending the platform

Adding a 7th module is just:
1. Create `modules/your_module.py` with a `render(provider, model_name)` function.
2. Add its label to `MODULES` in `config.py`.
3. Add one `elif` branch in `app.py`'s `main()`.

---

## 📌 Notes

- The included `data/sample.db` is a synthetic e-commerce dataset (10 customers, 12 products, random orders) generated by `scripts/build_sample_db.py` — safe to commit and demo with, no real data.
- FastEmbed downloads its embedding model from Hugging Face on first run and caches it locally afterward — you'll need internet access the first time you use Document Q&A.
- This project was built to demonstrate practical, end-to-end LLM application patterns (RAG, text-to-SQL, tool-augmented search, multi-modal input, memory management) rather than to be a production service — add authentication, rate-limiting, and persistent storage before deploying publicly.
