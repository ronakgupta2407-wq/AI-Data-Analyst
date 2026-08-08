import json

import pandas as pd
import plotly.express as px
import streamlit as st
from pypdf import PdfReader
from textwrap import dedent

from utils import ask_llm, generate_chart_instruction


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="DataMind AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Main background */
    .stApp {
        background: #f8fafc;
    }

    /* Main content */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* Hero */
    .hero {
        padding: 2.5rem;
        border-radius: 24px;
        background: linear-gradient(
            135deg,
            #111827 0%,
            #1e293b 50%,
            #334155 100%
        );
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 15px 35px rgba(15, 23, 42, 0.15);
    }

    .hero h1 {
        font-size: 3rem;
        margin-bottom: 0.5rem;
        font-weight: 800;
    }

    .hero p {
        font-size: 1.1rem;
        color: #cbd5e1;
        margin-bottom: 0;
    }

    /* Section headings */
    .section-title {
        font-size: 1.45rem;
        font-weight: 750;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        color: #111827;
    }

    /* Metric cards */
    .metric-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.25rem;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
        min-height: 120px;
    }

    .metric-label {
        color: #64748b;
        font-size: 0.9rem;
        margin-bottom: 0.4rem;
    }

    .metric-value {
        color: #0f172a;
        font-size: 1.8rem;
        font-weight: 750;
    }

    /* Upload box */
    [data-testid="stFileUploader"] {
        background: white;
        border-radius: 18px;
        padding: 1rem;
        border: 1px solid #e2e8f0;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #ffffff;
    }

    /* Chat */
    [data-testid="stChatMessage"] {
        border-radius: 14px;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HERO HEADER
# ============================================================

hero_html = dedent(
    """
    <div class="hero">
        <h1>📊 DataMind AI</h1>
        <p>
            Upload your data, ask questions in plain English,
            discover insights and generate interactive visualizations.
        </p>
    </div>
    """
)

st.markdown(hero_html, unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 📊 DataMind AI")

    st.caption(
        "Your AI-powered data analysis assistant."
    )

    st.divider()

    st.markdown("### 📂 Supported Files")

    st.markdown(
        """
        📄 **CSV**

        📊 **Excel**

        📕 **PDF**
        """
    )

    st.divider()

    st.markdown("### 💡 Try asking")

    st.caption("Dataset questions")

    st.markdown(
        """
        • Who has the highest value?

        • What is the average?

        • Find the top 5 records.

        • Which category performs best?

        • Show a bar chart.
        """
    )

    st.divider()

    st.caption("Powered by Ronak Gupta")


# ============================================================
# UPLOAD SECTION
# ============================================================

st.markdown(
    '<div class="section-title">📂 Upload your dataset</div>',
    unsafe_allow_html=True,
)

st.write(
    "Upload a CSV, Excel spreadsheet, or PDF document to begin."
)

uploaded_file = st.file_uploader(
    "Choose a file",
    type=["csv", "xlsx", "pdf"],
    label_visibility="collapsed",
)


# ============================================================
# NO FILE STATE
# ============================================================

if uploaded_file is None:

    st.markdown(
        """
        <h2 style="text-align:center;">
            📁 Upload a dataset to get started
        </h2>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <p style="text-align:center; color:#6b7280;">
            Ask questions, discover insights and generate
            interactive visualizations using AI.
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "📂 Upload a CSV, Excel spreadsheet, or PDF document above to begin."
    )

    st.stop()


# ============================================================
# READ FILE
# ============================================================

file_name = uploaded_file.name.lower()

try:

    if file_name.endswith(".csv"):

        df = pd.read_csv(uploaded_file)
        file_type = "data"

    elif file_name.endswith(".xlsx"):

        df = pd.read_excel(uploaded_file)
        file_type = "data"

    elif file_name.endswith(".pdf"):

        reader = PdfReader(uploaded_file)

        pdf_text = ""

        for page in reader.pages:

            text = page.extract_text()

            if text:
                pdf_text += text + "\n"

        file_type = "pdf"

    else:

        st.error("Unsupported file type.")
        st.stop()

except Exception as e:

    st.error(
        f"Unable to read the uploaded file: {str(e)}"
    )

    st.stop()


# ============================================================
# FILE INFORMATION
# ============================================================

st.success(
    f"✓ {uploaded_file.name} uploaded successfully"
)


# ============================================================
# CSV / EXCEL
# ============================================================

if file_type == "data":

    # --------------------------------------------------------
    # DATASET OVERVIEW
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">📈 Dataset Overview</div>',
        unsafe_allow_html=True,
    )

    rows = df.shape[0]
    columns = df.shape[1]
    missing = int(df.isnull().sum().sum())

    col1, col2, col3, col4 = st.columns(4)

    # --------------------------------------------------------
    # ROWS
    # --------------------------------------------------------

    with col1:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Total Rows</div>
                <div class="metric-value">{rows:,}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # COLUMNS
    # --------------------------------------------------------

    with col2:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Total Columns</div>
                <div class="metric-value">{columns:,}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # MISSING VALUES
    # --------------------------------------------------------

    with col3:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Missing Values</div>
                <div class="metric-value">{missing:,}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # FILE TYPE
    # --------------------------------------------------------

    with col4:

        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-label">File Type</div>
                <div class="metric-value">Data</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # DATASET PREVIEW
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">📋 Dataset Preview</div>',
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(
        ["📋 Data", "🔎 Column Information"]
    )

    with tab1:

        st.dataframe(
            df,
            use_container_width=True,
            height=400,
        )

    with tab2:

        info_df = pd.DataFrame(
            {
                "Column": df.columns,
                "Data Type": [
                    str(dtype)
                    for dtype in df.dtypes
                ],
                "Missing Values": [
                    int(df[column].isnull().sum())
                    for column in df.columns
                ],
            }
        )

        st.dataframe(
            info_df,
            use_container_width=True,
            hide_index=True,
        )

    # --------------------------------------------------------
    # AI ANALYST
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">🤖 Ask your AI Analyst</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Ask questions about your dataset in plain English."
    )

    question = st.chat_input(
        "e.g. Show the top 5 records by marks..."
    )

    if question:

        with st.chat_message(
            "user",
            avatar="👤",
        ):

            st.write(question)

        with st.chat_message(
            "assistant",
            avatar="🤖",
        ):

            with st.spinner(
                "AI is analyzing your dataset..."
            ):

                # ------------------------------------------------
                # AI ANSWER
                # ------------------------------------------------

                prompt = f"""
You are an AI Data Analyst.

Analyze the dataset and answer the user's question.

Dataset columns:

{list(df.columns)}

Dataset sample:

{df.head(10).to_string()}

User question:

{question}

Rules:

- Do NOT provide Python code.
- Do NOT show SQL queries.
- Do NOT explain your analysis process.
- Give only the final answer.
- Use simple English.
- Keep the answer concise.
"""

                try:

                    answer = ask_llm(prompt)

                    st.write(answer)

                except Exception as e:

                    st.error(
                        f"Unable to get AI response: {str(e)}"
                    )

                # ------------------------------------------------
                # CHART GENERATION
                # ------------------------------------------------

                try:

                    chart_response = generate_chart_instruction(
                        list(df.columns),
                        question,
                    )

                    # Remove accidental markdown fences
                    chart_response = (
                        chart_response
                        .replace("```json", "")
                        .replace("```", "")
                        .strip()
                    )

                    chart_data = json.loads(
                        chart_response
                    )

                    chart_type = chart_data.get(
                        "chart",
                        "none",
                    )

                    x = chart_data.get("x")
                    y = chart_data.get("y")

                    if (
                        chart_type != "none"
                        and x in df.columns
                        and y in df.columns
                    ):

                        st.markdown(
                            "### 📊 Visualization"
                        )

                        if chart_type == "bar":

                            fig = px.bar(
                                df,
                                x=x,
                                y=y,
                                title=f"{y} by {x}",
                            )

                        elif chart_type == "line":

                            fig = px.line(
                                df,
                                x=x,
                                y=y,
                                title=f"{y} by {x}",
                            )

                        elif chart_type == "pie":

                            fig = px.pie(
                                df,
                                names=x,
                                values=y,
                                title=f"{y} by {x}",
                            )

                        elif chart_type == "scatter":

                            fig = px.scatter(
                                df,
                                x=x,
                                y=y,
                                title=f"{y} vs {x}",
                            )

                        else:

                            fig = None

                        if fig:

                            fig.update_layout(
                                template="plotly_white",
                                margin=dict(
                                    l=20,
                                    r=20,
                                    t=60,
                                    b=20,
                                ),
                            )

                            st.plotly_chart(
                                fig,
                                use_container_width=True,
                            )

                except Exception:
                    # Chart generation should never
                    # prevent the AI answer from showing.
                    pass


# ============================================================
# PDF
# ============================================================

elif file_type == "pdf":

    st.markdown(
        '<div class="section-title">📕 PDF Document</div>',
        unsafe_allow_html=True,
    )

    if not pdf_text.strip():

        st.error(
            "Unable to extract text from this PDF."
        )

        st.stop()

    # --------------------------------------------------------
    # PDF STATISTICS
    # --------------------------------------------------------

    word_count = len(
        pdf_text.split()
    )

    character_count = len(
        pdf_text
    )

    col1, col2, col3 = st.columns(3)

    # --------------------------------------------------------
    # WORDS
    # --------------------------------------------------------

    with col1:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Words</div>
                <div class="metric-value">{word_count:,}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # CHARACTERS
    # --------------------------------------------------------

    with col2:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Characters</div>
                <div class="metric-value">{character_count:,}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # FILE TYPE
    # --------------------------------------------------------

    with col3:

        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-label">File Type</div>
                <div class="metric-value">PDF</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # PDF PREVIEW
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">📄 Document Preview</div>',
        unsafe_allow_html=True,
    )

    with st.expander(
        "👀 View extracted text"
    ):

        st.text_area(
            "PDF content",
            pdf_text[:15000],
            height=400,
            label_visibility="collapsed",
        )

    # --------------------------------------------------------
    # PDF AI
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">🤖 Ask about this PDF</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Ask questions about the uploaded document."
    )

    question = st.chat_input(
        "e.g. Summarize this document..."
    )

    if question:

        with st.chat_message(
            "user",
            avatar="👤",
        ):

            st.write(question)

        with st.chat_message(
            "assistant",
            avatar="🤖",
        ):

            with st.spinner(
                "AI is reading the document..."
            ):

                prompt = f"""
You are an AI Data Analyst.

Analyze the following PDF content.

PDF content:

{pdf_text[:15000]}

User question:

{question}

Rules:

- Do NOT provide Python code.
- Do NOT show SQL.
- Do NOT explain your reasoning.
- Give only the final answer.
- Use simple English.
- Keep the answer concise.
"""

                try:

                    answer = ask_llm(prompt)

                    st.write(answer)

                except Exception as e:

                    st.error(
                        f"Unable to get AI response: {str(e)}"
                    )