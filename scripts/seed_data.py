import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.connection import get_db_connection

# =================================================
# SKILLS (EXPANDED, ATS-FRIENDLY)
# =================================================
SKILLS = [
    # Programming
    "Python", "Java", "C++", "JavaScript",

    # Backend / APIs
    "Flask", "Django", "REST APIs", "Spring Boot",

    # Databases
    "MySQL", "PostgreSQL", "MongoDB",

    # Data / ML
    "Machine Learning", "Data Analysis", "Power BI",

    # Cloud / DevOps
    "AWS", "Docker", "Git",

    # Frontend
    "HTML", "CSS", "React"
]

# =================================================
# JOB TEMPLATES (CORE ROLES)
# =================================================
JOB_TEMPLATES = {
    "Backend Developer": ["Python", "MySQL", "Flask", "REST APIs"],
    "Backend Intern": ["Python", "MySQL", "Flask"],

    "Java Backend Developer": ["Java", "Spring Boot", "MySQL"],
    "API Developer": ["Python", "REST APIs", "PostgreSQL"],

    "Frontend Developer": ["HTML", "CSS", "JavaScript", "React"],
    "Full Stack Developer": ["Python", "React", "REST APIs", "MySQL"],

    "Data Analyst": ["SQL", "Data Analysis", "Power BI"],
    "Data Analyst Intern": ["SQL", "Data Analysis"],

    "ML Engineer": ["Python", "Machine Learning", "AWS"],
    "ML Intern": ["Python", "Machine Learning"],

    "Cloud Engineer": ["AWS", "Docker"],
    "DevOps Engineer": ["AWS", "Docker", "Git"],

    "Python Developer": ["Python", "Git", "MySQL"],
    "C++ Developer": ["C++", "Data Structures"]
}

# =================================================
# EXPERIENCE VARIANTS (AUTO-GENERATE JOBS)
# =================================================
EXPERIENCE_VARIANTS = [
    ("Intern", 0),
    ("Junior", 1),
    ("Mid", 2),
    ("Senior", 3)
]

# =================================================
# SEED FUNCTIONS
# =================================================
def seed_skills(cursor):
    for skill in SKILLS:
        cursor.execute(
            "INSERT IGNORE INTO skills (skill_name) VALUES (%s)",
            (skill,)
        )

def seed_jobs_and_skills(cursor):
    cursor.execute("SELECT id, skill_name FROM skills")
    skill_map = {name: sid for sid, name in cursor.fetchall()}

    for base_title, skills in JOB_TEMPLATES.items():
        for level, min_exp in EXPERIENCE_VARIANTS:

            # Intern logic
            if "Intern" in base_title and level != "Intern":
                continue
            if "Intern" not in base_title and level == "Intern":
                continue

            title = f"{base_title} ({level})"

            cursor.execute(
                "INSERT INTO jobs (title, min_experience) VALUES (%s, %s)",
                (title, min_exp)
            )
            job_id = cursor.lastrowid

            for skill in skills:
                if skill in skill_map:
                    cursor.execute(
                        "INSERT INTO job_skills (job_id, skill_id) VALUES (%s, %s)",
                        (job_id, skill_map[skill])
                    )

# =================================================
# MAIN
# =================================================
def main():
    conn = get_db_connection()
    cursor = conn.cursor(buffered=True)

    seed_skills(cursor)
    seed_jobs_and_skills(cursor)

    conn.commit()
    cursor.close()
    conn.close()

    print("✅ Database seeded with expanded skills & ~100 jobs")

if __name__ == "__main__":
    main()
