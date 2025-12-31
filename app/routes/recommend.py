from flask import Blueprint, jsonify, request
from app.services.recommender import get_recommendations_by_skills

recommend_bp = Blueprint("recommend", __name__)

@recommend_bp.route("/recommend-by-skills", methods=["POST"])
def recommend_by_skills():
    """
    Recommend jobs based on skills and experience
    """

    data = request.get_json()

    skills_input = data.get("skills", "")
    experience = int(data.get("experience", 2))

    skills = {s.strip() for s in skills_input.split(",") if s.strip()}

    recommendations = get_recommendations_by_skills(
        skills,
        user_experience=experience
    )

    return jsonify({
        "input_skills": list(skills),
        "experience": experience,
        "recommendations": recommendations
    })
