import re
from .fallback_data import FALLBACK_JOBS


def normalize(skills):
    return {s.strip().lower() for s in skills if s.strip()}


def normalize_title(title: str):
    return re.sub(r"\s*\(.*?\)", "", title).strip().lower()


def get_from_db(user_skills_set, experience):
    from recommender.models import Job

    results = []
    jobs = Job.objects.filter(min_experience__lte=experience).prefetch_related("skills")

    for job in jobs:
        job_skills = {s.name.lower() for s in job.skills.all()}
        if not job_skills:
            continue
        matched = user_skills_set & job_skills
        if not matched:
            continue
        score = round(len(matched) / len(job_skills), 3)
        results.append({
            "title": job.title,
            "min_experience": job.min_experience,
            "matched_skills": list(matched),
            "missing_skills": sorted(job_skills - user_skills_set),
            "score": score,
        })

    return results


def get_from_fallback(user_skills_set, experience):
    results = []
    for job in FALLBACK_JOBS:
        if job["min_experience"] > experience:
            continue
        job_skills = {s.lower() for s in job["skills"]}
        matched = user_skills_set & job_skills
        if not matched:
            continue
        score = round(len(matched) / len(job_skills), 3)
        results.append({
            "title": job["title"],
            "min_experience": job["min_experience"],
            "matched_skills": list(matched),
            "missing_skills": sorted(job_skills - user_skills_set),
            "score": score,
        })
    return results


def get_recommendations_by_skills(user_skills, experience):
    user_skills_set = normalize(user_skills)
    combined = {}

    try:
        db_results = get_from_db(user_skills_set, experience)
    except Exception as e:
        print(f"⚠️ DB unavailable, using fallback: {e}")
        db_results = []

    for source in (db_results, get_from_fallback(user_skills_set, experience)):
        for job in source:
            key = normalize_title(job["title"])
            if key not in combined:
                combined[key] = job
            elif job["score"] > combined[key]["score"]:
                combined[key] = job
            else:
                combined[key]["matched_skills"] = list(
                    set(combined[key]["matched_skills"]) | set(job["matched_skills"])
                )
                combined[key]["missing_skills"] = sorted(
                    set(combined[key].get("missing_skills", [])) &
                    set(job.get("missing_skills", []))
                )

    return sorted(combined.values(), key=lambda x: x["score"], reverse=True)
