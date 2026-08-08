import os

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


@st.cache_resource
def get_groq_client():
    """
    Create and cache the Groq client.

    Works both:
    - Locally using .env
    - On Streamlit Cloud using Secrets
    """

    api_key = os.getenv("GROQ_API_KEY")

    # Streamlit Cloud Secrets
    if not api_key:
        try:
            api_key = st.secrets["GROQ_API_KEY"]
        except Exception:
            api_key = None

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. "
            "Add GROQ_API_KEY to your .env file locally "
            "or to Streamlit Cloud Secrets."
        )

    return Groq(api_key=api_key)


def ask_llm(prompt):
    """
    Send a prompt to Groq and return the response.
    """

    client = get_groq_client()

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content


def generate_chart_instruction(columns, question):
    """
    Ask the LLM whether a chart is appropriate and,
    if so, return chart configuration as JSON.
    """

    prompt = f"""
You are a data visualization expert.

The dataset has these columns:

{columns}

The user asked:

{question}

Decide whether a chart would help answer the user's question.

Return ONLY valid JSON.

Do not use markdown.
Do not use ```json.
Do not add explanations outside the JSON.

The JSON must have exactly this structure:

{{
    "chart": "bar",
    "x": "column_name",
    "y": "column_name"
}}

If a chart is not appropriate, return:

{{
    "chart": "none",
    "x": null,
    "y": null
}}

Allowed chart types:
- bar
- line
- pie
- scatter
- none

The x and y values MUST be column names from the dataset.

User question:
{question}
"""

    return ask_llm(prompt)