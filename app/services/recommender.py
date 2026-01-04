from app.db.connection import get_db_connection
from app.services.fallback_data import FALLBACK_JOBS
import re


# =================================================
# HELPERS
# =================================================

def normalize(skills):
    return {s.strip().lower() for s in skills if s.strip()}


def normalize_title(title: str):
    """
    Removes experience suffixes like:
    (Junior), (Intern), (Senior)
    """
    return re.sub(r"\s*\(.*?\)", "", title).strip().lower()


# =================================================
# SQL SOURCE
# =================================================

def get_from_sql(user_skills, experience):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT
            j.title,
            j.min_experience,
            s.skill_name
        FROM jobs j
        JOIN job_skills js ON j.id = js.job_id
        JOIN skills s ON js.skill_id = s.id
        WHERE j.min_experience <= %s
    """

    cursor.execute(query, (experience,))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    jobs = {}

    for row in rows:
        title = row["title"]
        base_title = normalize_title(title)
        skill = row["skill_name"].lower()

        if base_title not in jobs:
            jobs[base_title] = {
                "title": title,  # keep display title
                "min_experience": row["min_experience"],
                "matched_skills": set(),
                "total_skills": set(),
            }

        jobs[base_title]["total_skills"].add(skill)

        if skill in user_skills:
            jobs[base_title]["matched_skills"].add(skill)

    results = []
    for job in jobs.values():
        if not job["matched_skills"]:
            continue

        score = round(
            len(job["matched_skills"]) / len(job["total_skills"]),
            3
        )

        results.append({
            "title": job["title"],
            "min_experience": job["min_experience"],
            "matched_skills": list(job["matched_skills"]),
            "score": score,
        })

    return results


# =================================================
# FALLBACK SOURCE
# =================================================

def get_from_fallback(user_skills, experience):
    results = []

    for job in FALLBACK_JOBS:
        if job["min_experience"] > experience:
            continue

        job_skills = {s.lower() for s in job["skills"]}
        matched = user_skills & job_skills

        if not matched:
            continue

        score = round(len(matched) / len(job_skills), 3)

        results.append({
            "title": job["title"],
            "min_experience": job["min_experience"],
            "matched_skills": list(matched),
            "score": score,
        })

    return results


# =================================================
# MAIN ENGINE (NO DUPLICATES GUARANTEED)
# =================================================

def get_recommendations_by_skills(user_skills, experience):
    user_skills = normalize(user_skills)
    combined = {}

    try:
        sql_results = get_from_sql(user_skills, experience)
    except Exception as e:
        print("⚠️ SQL unavailable, fallback only:", e)
        sql_results = []

    fallback_results = get_from_fallback(user_skills, experience)

    for source in (sql_results, fallback_results):
        for job in source:
            base_title = normalize_title(job["title"])
            key = base_title

            if key not in combined:
                combined[key] = job
            else:
                # keep higher score
                if job["score"] > combined[key]["score"]:
                    combined[key] = job
                else:
                    combined[key]["matched_skills"] = list(
                        set(combined[key]["matched_skills"]) |
                        set(job["matched_skills"])
                    )

    return sorted(
        combined.values(),
        key=lambda x: x["score"],
        reverse=True
    )
