import os
from dotenv import load_dotenv
from groq import Groq


load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY not found in .env file"
    )

client = Groq(
    api_key=api_key
)


def ask_llm(prompt):

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_tokens=1024
    )

    return response.choices[0].message.content


def generate_chart_instruction(columns, question):

    prompt = f"""
You are a data analyst.

Dataset columns:
{columns}

User question:
{question}

Rules:
- Return only JSON.
- No explanation.
- No markdown.
- No code blocks.

Decide if a chart is needed.

If a chart is needed, return:

{{
    "chart": "bar",
    "x": "column_name",
    "y": "column_name"
}}

Available charts:
bar
line
scatter
pie

If no chart is needed, return:

{{
    "chart": "none"
}}
"""

    response = ask_llm(prompt)

    return response