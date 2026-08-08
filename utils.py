import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


@st.cache_resource
def get_groq_client():

    api_key = os.getenv("GROQ_API_KEY")

    # Streamlit Cloud secrets
    if not api_key:
        api_key = st.secrets.get("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. "
            "Add it to Streamlit Cloud Secrets."
        )

    return Groq(api_key=api_key)


def ask_llm(prompt):
    client = get_groq_client()

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content