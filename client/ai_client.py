from groq import Groq
from decouple import config

client = Groq(
    api_key=config("GROQ_API_KEY")
)

SYSTEM_PROMPT = """
When asked about GitHub or Notion, take reference/data from the GitHub and Notion MCP.
Do not generate answers without MCP reference/data.
"""


def ask_llm(prompt):
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content
