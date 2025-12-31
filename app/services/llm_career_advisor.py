import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def get_career_advice(role: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return "Groq API key not configured."

    client = Groq(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional career advisor."
                },
                {
                    "role": "user",
                    "content": f"List core skills required for a {role}. Bullet points only."
                }
            ],
            temperature=0.3,
            max_tokens=300
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"LLM error: {str(e)}"
