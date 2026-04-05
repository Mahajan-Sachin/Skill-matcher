import re
from .fallback_data import FALLBACK_JOBS


# =====================
# HELPERS
# =====================

def normalize(skills):
    """Lowercase and strip a list of skill strings into a set."""
    return {s.strip().lower() for s in skills if s.strip()}


def normalize_title(title: str):
    """Strip experience suffixes like (Junior), (Senior) for deduplication."""
    return re.sub(r"\s*\(.*?\)", "", title).strip().lower()


# =====================
# DB SOURCE (Django ORM)
# =====================

def get_from_db(user_skills_set, experience):
    from recommender.models import Job  # import inside to avoid circular issues

    results = []
    jobs = Job.objects.filter(min_experience__lte=experience).prefetch_related("skills")

    for job in jobs:
        job_skills = {s.name.lower() for s in job.skills.all()}
        if not job_skills:
            continue
        matched = user_skills_set & job_skills
        if not matched:
            continue
        missing = job_skills - user_skills_set   # ← skills gap
        score = round(len(matched) / len(job_skills), 3)
        results.append({
            "title": job.title,
            "min_experience": job.min_experience,
            "matched_skills": list(matched),
            "missing_skills": sorted(missing),   # ← what to learn next
            "score": score,
        })

    return results


# =====================
# FALLBACK SOURCE
# =====================

def get_from_fallback(user_skills_set, experience):
    results = []
    for job in FALLBACK_JOBS:
        if job["min_experience"] > experience:
            continue
        job_skills = {s.lower() for s in job["skills"]}
        matched = user_skills_set & job_skills
        if not matched:
            continue
        missing = job_skills - user_skills_set
        score = round(len(matched) / len(job_skills), 3)
        results.append({
            "title": job["title"],
            "min_experience": job["min_experience"],
            "matched_skills": list(matched),
            "missing_skills": sorted(missing),
            "score": score,
        })
    return results


# =====================
# MAIN ENGINE
# =====================

def get_recommendations_by_skills(user_skills, experience):
    user_skills_set = normalize(user_skills)
    combined = {}

    try:
        db_results = get_from_db(user_skills_set, experience)
    except Exception as e:
        print(f"⚠️ DB unavailable, using fallback only: {e}")
        db_results = []

    fallback_results = get_from_fallback(user_skills_set, experience)

    for source in (db_results, fallback_results):
        for job in source:
            key = normalize_title(job["title"])
            if key not in combined:
                combined[key] = job
            else:
                # Keep the higher score entry; merge matched skills
                if job["score"] > combined[key]["score"]:
                    combined[key] = job
                else:
                    combined[key]["matched_skills"] = list(
                        set(combined[key]["matched_skills"]) | set(job["matched_skills"])
                    )
                    # Recompute missing based on merged matched
                    combined[key]["missing_skills"] = sorted(
                        set(combined[key].get("missing_skills", [])) &
                        set(job.get("missing_skills", []))
                    )

    return sorted(combined.values(), key=lambda x: x["score"], reverse=True)
