import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


@st.cache_resource
def get_groq_client():
    # Try environment variable first
    api_key = os.getenv("GROQ_API_KEY")

    # If not found, try Streamlit Cloud Secrets
    if not api_key:
        try:
            api_key = st.secrets["GROQ_API_KEY"]
        except Exception:
            api_key = None

    # Stop if API key is missing
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. "
            "Add it to your .env file locally or "
            "Streamlit Cloud Secrets when deployed."
        )

    return Groq(api_key=api_key)


def ask_llm(prompt):
    client = get_groq_client()

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content


def generate_chart_instruction(data):
    prompt = f"""
You are a data visualization expert.

Analyze the following dataset:

{data}

Determine the most appropriate chart for this data.

Return:
1. Chart type
2. X-axis column
3. Y-axis column
4. A short explanation of why this chart is appropriate

Keep the response concise.
"""

    return ask_llm(prompt)