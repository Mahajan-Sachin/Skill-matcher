from app.db.connection import get_db_connection

from app.services.fallback_data import FALLBACK_JOBS

def get_recommendations_by_skills(skills, user_experience):
    recommendations = []

    try:
        # -----------------------------
        # TRY DATABASE FIRST
        # -----------------------------
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT j.id, j.title, j.min_experience
            FROM jobs j
        """)
        jobs = cursor.fetchall()

        for job in jobs:
            cursor.execute("""
                SELECT s.skill_name
                FROM job_skills js
                JOIN skills s ON js.skill_id = s.id
                WHERE js.job_id = %s
            """, (job["id"],))
            job_skills = {row["skill_name"] for row in cursor.fetchall()}

            matched = skills.intersection(job_skills)
            score = len(matched) / len(job_skills) if job_skills else 0

            if user_experience >= job["min_experience"] and score > 0:
                recommendations.append({
                    "title": job["title"],
                    "matched_skills": list(matched),
                    "score": round(score, 3),
                    "min_experience": job["min_experience"],
                    "role_type": "Intern" if job["min_experience"] == 0 else "Junior"
                })

        cursor.close()
        conn.close()

    except Exception:
        # -----------------------------
        # FALLBACK MODE (NO DB)
        # -----------------------------
        for job in FALLBACK_JOBS:
            matched = skills.intersection(job["skills"])
            score = len(matched) / len(job["skills"])

            if user_experience >= job["min_experience"] and score > 0:
                recommendations.append({
                    "title": job["title"],
                    "matched_skills": list(matched),
                    "score": round(score, 3),
                    "min_experience": job["min_experience"],
                    "role_type": job["role_type"]
                })

    recommendations.sort(key=lambda x: x["score"], reverse=True)
    return recommendations
