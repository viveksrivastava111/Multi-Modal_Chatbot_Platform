"""
SQL Query Assistant module.

Lets the user ask plain-English questions about a database. The LLM is
shown the schema, writes a SQL query, we execute it against SQLite,
and the LLM then explains the result in plain English. Ships with a
small sample e-commerce database so it works out of the box.
"""
import re
import sqlite3

import pandas as pd
import streamlit as st
from langchain_core.messages import SystemMessage, HumanMessage

from utils.llm_manager import get_llm
import config

SQL_SYSTEM_PROMPT = """You are a SQL expert. Given the database schema below, \
write a single SQLite query that answers the user's question.

Schema:
{schema}

Rules:
- Return ONLY the raw SQL query, no markdown fences, no explanation.
- Use only tables/columns that exist in the schema.
- Prefer LIMIT 50 for exploratory queries unless the user asks for everything.
"""

EXPLAIN_SYSTEM_PROMPT = (
    "You explain SQL query results to non-technical users in 2-4 clear sentences. "
    "Be specific about the numbers/rows you see."
)


def _get_schema(conn) -> str:
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]
    schema_parts = []
    for t in tables:
        cur.execute(f"PRAGMA table_info({t})")
        cols = ", ".join(f"{c[1]} ({c[2]})" for c in cur.fetchall())
        schema_parts.append(f"Table {t}: {cols}")
    return "\n".join(schema_parts)


def _extract_sql(text: str) -> str:
    text = text.strip()
    match = re.search(r"```(?:sql)?\s*(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text


def render(provider: str, model_name: str):
    st.subheader("🗃️ SQL Query Assistant")
    st.caption("Ask questions in plain English — the assistant writes and runs the SQL for you.")

    db_choice = st.radio(
        "Database source", ["Use sample database", "Upload your own .db/.sqlite file"],
        horizontal=True,
    )

    if db_choice == "Upload your own .db/.sqlite file":
        uploaded = st.file_uploader("Upload SQLite database", type=["db", "sqlite", "sqlite3"])
        if not uploaded:
            st.info("Upload a database file to continue.")
            return
        with open(config.SAMPLE_DB_PATH + ".user", "wb") as f:
            f.write(uploaded.getbuffer())
        db_path = config.SAMPLE_DB_PATH + ".user"
    else:
        db_path = config.SAMPLE_DB_PATH

    conn = sqlite3.connect(db_path)
    schema = _get_schema(conn)

    with st.expander("📋 View schema"):
        st.code(schema)

    question = st.text_input(
        "Ask a question about the data",
        placeholder="e.g. Which product category has the highest total revenue?",
    )
    ask = st.button("Run query", type="primary")

    if not (ask and question):
        return

    try:
        llm = get_llm(provider, model_name, temperature=0)

        # 1) Generate SQL
        sql_messages = [
            SystemMessage(content=SQL_SYSTEM_PROMPT.format(schema=schema)),
            HumanMessage(content=question),
        ]
        raw_sql = llm.invoke(sql_messages).content
        sql_query = _extract_sql(raw_sql)

        st.markdown("**Generated SQL:**")
        st.code(sql_query, language="sql")

        # 2) Execute
        df = pd.read_sql_query(sql_query, conn)
        st.markdown("**Result:**")
        st.dataframe(df, use_container_width=True)

        # 3) Explain
        if not df.empty:
            explain_messages = [
                SystemMessage(content=EXPLAIN_SYSTEM_PROMPT),
                HumanMessage(
                    content=f"Question: {question}\nQuery: {sql_query}\n"
                    f"Result (first rows): {df.head(10).to_dict(orient='records')}"
                ),
            ]
            explanation = llm.invoke(explain_messages).content
            st.markdown("**Explanation:**")
            st.write(explanation)
        else:
            st.info("The query returned no rows.")

    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        conn.close()
