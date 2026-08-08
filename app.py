
import json

import pandas as pd
import plotly.express as px
import streamlit as st
from pypdf import PdfReader

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
# HEADER
# ============================================================

st.title("📊 DataMind AI")

st.write(
    "Upload your data, ask questions in plain English, "
    "discover insights and generate interactive visualizations."
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("📊 DataMind AI")

    st.caption(
        "Your AI-powered data analysis assistant."
    )

    st.divider()

    st.subheader("📂 Supported Files")

    st.write("📄 CSV")
    st.write("📊 Excel")
    st.write("📕 PDF")

    st.divider()

    st.subheader("💡 Try asking")

    st.caption("Dataset questions")

    st.write("• Who has the highest value?")
    st.write("• What is the average?")
    st.write("• Find the top 5 records.")
    st.write("• Which category performs best?")
    st.write("• Show a bar chart.")

    st.divider()

    st.caption("Powered by Ronak Gupta")


# ============================================================
# UPLOAD SECTION
# ============================================================

st.header("📂 Upload your dataset")

st.write(
    "Upload a CSV, Excel spreadsheet, or PDF document to begin."
)

uploaded_file = st.file_uploader(
    "Choose a file",
    type=["csv", "xlsx", "pdf"],
)


# ============================================================
# NO FILE STATE
# ============================================================

if uploaded_file is None:

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

    st.header("📈 Dataset Overview")

    rows = df.shape[0]
    columns = df.shape[1]
    missing = int(df.isnull().sum().sum())

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Rows",
            f"{rows:,}",
        )

    with col2:
        st.metric(
            "Total Columns",
            f"{columns:,}",
        )

    with col3:
        st.metric(
            "Missing Values",
            f"{missing:,}",
        )

    with col4:
        st.metric(
            "File Type",
            "Data",
        )


    # --------------------------------------------------------
    # DATASET PREVIEW
    # --------------------------------------------------------

    st.header("📋 Dataset Preview")

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

    st.header("🤖 Ask your AI Analyst")

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

                        st.subheader("📊 Visualization")

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

    st.header("📕 PDF Document")

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

    with col1:

        st.metric(
            "Words",
            f"{word_count:,}",
        )

    with col2:

        st.metric(
            "Characters",
            f"{character_count:,}",
        )

    with col3:

        st.metric(
            "File Type",
            "PDF",
        )


    # --------------------------------------------------------
    # PDF PREVIEW
    # --------------------------------------------------------

    st.header("📄 Document Preview")

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

    st.header("🤖 Ask about this PDF")

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

