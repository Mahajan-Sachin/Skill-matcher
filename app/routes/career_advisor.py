from flask import Blueprint, request, jsonify
import os
from groq import Groq

career_bp = Blueprint("career_advisor", __name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

@career_bp.route("/career-advice", methods=["POST"])
def career_advice():
    data = request.get_json()
    role = data.get("role")
    custom_role = data.get("custom_role", "")

    final_role = custom_role.strip() if role == "OTHER" else role

    if not final_role:
        return jsonify({"error": "Role not provided."}), 400

    if not GROQ_API_KEY:
        return jsonify({
            "error": "Groq API key not configured."
        }), 200

    client = Groq(api_key=GROQ_API_KEY)

    prompt = f"""
You are a career advisor.

Explain for the role: {final_role}

1. Core technical skills required
2. Nice-to-have skills
3. Beginner learning focus
4. Common mistakes candidates make

Keep the response concise and structured.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=400
        )

        return jsonify({
            "advice": response.choices[0].message.content
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500
