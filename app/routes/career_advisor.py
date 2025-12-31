from flask import Blueprint, request, jsonify
from app.services.llm_career_advisor import get_career_advice

career_bp = Blueprint("career_advisor", __name__)

@career_bp.route("/career-advice", methods=["POST"])
def career_advice():
    data = request.get_json()
    role = data.get("role")

    if not role:
        return jsonify({"error": "Target role not provided"}), 400

    advice = get_career_advice(role)

    return jsonify({
        "role": role,
        "advice": advice
    })
