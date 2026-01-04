from flask import Blueprint, request, jsonify

from app.services.recommender import get_recommendations_by_skills

# =================================================
# BLUEPRINT (MUST EXIST)
# =================================================
recommend_bp = Blueprint("recommend", __name__)

# =================================================
# ROUTE
# =================================================
@recommend_bp.route("/recommend-by-skills", methods=["POST"])
def recommend_by_skills():
    data = request.get_json() or {}

    skills_input = data.get("skills", "")
    experience = int(data.get("experience", 0))

    user_skills = [
        s.strip() for s in skills_input.split(",") if s.strip()
    ]

    try:
        recommendations = get_recommendations_by_skills(
            user_skills=user_skills,
            experience=experience
        )
    except Exception as e:
        # absolute safety net (should not trigger if fallback works)
        return jsonify({
            "error": "Recommendation service unavailable",
            "details": str(e)
        }), 500

    return jsonify({
        "input_skills": user_skills,
        "experience": experience,
        "recommendations": recommendations
    })
