import streamlit as st
import pandas as pd
import plotly.express as px
import json

from pypdf import PdfReader
from utils import ask_llm, generate_chart_instruction
from textwrap import dedent


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="DataMind AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

.info-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 15px;
    padding: 25px;
    text-align: center;
}

.card-title {
    font-size: 16px;
    font-weight: 600;
    color: #64748b;
}

.card-value {
    font-size: 30px;
    font-weight: 700;
    color: #111827;
}

.section-title {
    font-size: 24px;
    font-weight: 700;
    margin-top: 25px;
    margin-bottom: 15px;
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# HERO HEADER
# ============================================================

hero_html = dedent(
    """
<h1>📊 DataMind AI</h1>
<p>Upload your dataset or PDF and ask questions using AI.</p>
"""
)

st.markdown(
    hero_html,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
<h2>📊 DataMind AI</h2>
""",
        unsafe_allow_html=True
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
    "📂 Upload your dataset",
    unsafe_allow_html=True
)

st.write(
    "Upload a CSV, Excel spreadsheet, or PDF document to begin."
)

uploaded_file = st.file_uploader(
    "Choose a file",
    type=["csv", "xlsx", "pdf"],
    label_visibility="collapsed"
)


# ============================================================
# NO FILE STATE
# ============================================================

if uploaded_file is None:

    st.markdown(
        "<h2 style='text-align:center;'>📁 Upload a dataset to get started</h2>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='text-align:center; color:#6b7280;'>"
        "Ask questions, discover insights and generate "
        "interactive visualizations using AI."
        "</p>",
        unsafe_allow_html=True
    )

    st.info(
        "📂 Upload a CSV, Excel spreadsheet, or PDF document above to begin."
    )

    st.stop()


# ============================================================
# READ FILE
# ============================================================

file_name = uploaded_file.name.lower()

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
        unsafe_allow_html=True
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
<div class="info-card">
<div class="card-title">Rows</div>
<div class="card-value">{rows:,}</div>
</div>
""",
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # COLUMNS
    # --------------------------------------------------------

    with col2:

        st.markdown(
            f"""
<div class="info-card">
<div class="card-title">Columns</div>
<div class="card-value">{columns}</div>
</div>
""",
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # MISSING VALUES
    # --------------------------------------------------------

    with col3:

        st.markdown(
            f"""
<div class="info-card">
<div class="card-title">Missing Values</div>
<div class="card-value">{missing:,}</div>
</div>
""",
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # FILE TYPE
    # --------------------------------------------------------

    with col4:

        st.markdown(
            """
<div class="info-card">
<div class="card-title">File Type</div>
<div class="card-value">DATA</div>
</div>
""",
            unsafe_allow_html=True
        )


    # --------------------------------------------------------
    # DATASET PREVIEW
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">📋 Dataset Preview</div>',
        unsafe_allow_html=True
    )

    tab1, tab2 = st.tabs(
        ["📋 Data", "🔎 Column Information"]
    )

    with tab1:

        st.dataframe(
            df,
            use_container_width=True,
            height=400
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
                ]
            }
        )

        st.dataframe(
            info_df,
            use_container_width=True,
            hide_index=True
        )


    # --------------------------------------------------------
    # AI ANALYST
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">🤖 Ask your AI Analyst</div>',
        unsafe_allow_html=True
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
            avatar="👤"
        ):

            st.write(question)

        with st.chat_message(
            "assistant",
            avatar="🤖"
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

                answer = ask_llm(prompt)

                st.write(answer)


                # ------------------------------------------------
                # CHART GENERATION
                # ------------------------------------------------

                chart_response = generate_chart_instruction(
                    list(df.columns),
                    question
                )

                try:

                    chart_data = json.loads(
                        chart_response
                    )

                    chart_type = chart_data.get(
                        "chart",
                        "none"
                    )

                    if chart_type != "none":

                        x = chart_data.get("x")
                        y = chart_data.get("y")

                        if (
                            x in df.columns
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
                                    title=f"{y} by {x}"
                                )

                            elif chart_type == "line":

                                fig = px.line(
                                    df,
                                    x=x,
                                    y=y,
                                    title=f"{y} by {x}"
                                )

                            elif chart_type == "pie":

                                fig = px.pie(
                                    df,
                                    names=x,
                                    values=y,
                                    title=f"{y} by {x}"
                                )

                            elif chart_type == "scatter":

                                fig = px.scatter(
                                    df,
                                    x=x,
                                    y=y,
                                    title=f"{y} vs {x}"
                                )

                            else:

                                fig = None

                            if fig:

                                st.plotly_chart(
                                    fig,
                                    use_container_width=True
                                )

                except Exception:

                    pass


# ============================================================
# PDF
# ============================================================

elif file_type == "pdf":

    st.markdown(
        '<div class="section-title">📕 PDF Document</div>',
        unsafe_allow_html=True
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
<div class="info-card">
<div class="card-title">Words</div>
<div class="card-value">{word_count:,}</div>
</div>
""",
            unsafe_allow_html=True
        )


    # --------------------------------------------------------
    # CHARACTERS
    # --------------------------------------------------------

    with col2:

        st.markdown(
            f"""
<div class="info-card">
<div class="card-title">Characters</div>
<div class="card-value">{character_count:,}</div>
</div>
""",
            unsafe_allow_html=True
        )


    # --------------------------------------------------------
    # FILE TYPE
    # --------------------------------------------------------

    with col3:

        st.markdown(
            """
<div class="info-card">
<div class="card-title">File Type</div>
<div class="card-value">PDF</div>
</div>
""",
            unsafe_allow_html=True
        )


    # --------------------------------------------------------
    # PDF PREVIEW
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">📄 Document Preview</div>',
        unsafe_allow_html=True
    )

    with st.expander(
        "👀 View extracted text"
    ):

        st.text_area(
            "PDF content",
            pdf_text[:15000],
            height=400,
            label_visibility="collapsed"
        )


    # --------------------------------------------------------
    # PDF AI
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">🤖 Ask about this PDF</div>',
        unsafe_allow_html=True
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
            avatar="👤"
        ):

            st.write(question)

        with st.chat_message(
            "assistant",
            avatar="🤖"
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

                answer = ask_llm(prompt)

                st.write(answer)