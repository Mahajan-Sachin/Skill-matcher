import os
import requests
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_API_TOKEN")

HF_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
HF_URL = f"https://router.huggingface.co/hf-inference/models/{HF_MODEL}"

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

def get_career_advice(target_role: str):
    if not HF_TOKEN:
        return {"error": "Hugging Face API token not configured."}

    prompt = f"""
You are a career advisor for a tech company.

Explain clearly:
1. Core skills required for a {target_role}
2. Nice-to-have skills
3. What beginners should focus on first
4. Common mistakes candidates make

Keep the answer concise and structured.
"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 300,
            "temperature": 0.4
        }
    }

    try:
        response = requests.post(
            HF_URL,
            headers=HEADERS,
            json=payload,
            timeout=60
        )

        if response.status_code != 200:
            return {"error": f"HF API error: {response.text}"}

        data = response.json()

        # HF router response format
        if isinstance(data, list) and "generated_text" in data[0]:
            return {"advice": data[0]["generated_text"]}

        return {"error": "Unexpected response from AI model."}

    except Exception as e:
        return {"error": str(e)}
