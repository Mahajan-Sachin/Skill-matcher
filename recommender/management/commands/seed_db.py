from django.core.management.base import BaseCommand
from recommender.models import Skill, Job


SKILLS = [
    # Programming Languages
    "Python", "Java", "C++", "JavaScript", "TypeScript",
    "Go", "Rust", "Kotlin", "Swift", "R", "Scala",

    # Backend / APIs
    "Flask", "Django", "FastAPI", "REST APIs", "Spring Boot", "Node.js", "Express.js",

    # Frontend
    "HTML", "CSS", "React", "Vue.js", "Angular", "Next.js",

    # Databases
    "MySQL", "PostgreSQL", "MongoDB", "SQL", "Redis", "SQLite", "Cassandra",

    # ML / AI / Data Science
    "Machine Learning", "Deep Learning", "Data Analysis",
    "Scikit-learn", "TensorFlow", "PyTorch", "Keras",
    "NLP", "Computer Vision", "Pandas", "NumPy",
    "Matplotlib", "Seaborn", "Jupyter", "Power BI",
    "Hugging Face", "LangChain", "OpenCV",

    # Systems / Core CS
    "Data Structures", "Algorithms", "Operating Systems", "Networking",
    "System Design", "OOP",

    # Cloud / DevOps
    "AWS", "GCP", "Azure", "Docker", "Kubernetes", "Git",
    "CI/CD", "Linux", "Terraform", "Ansible",
]


JOB_TEMPLATES = {
    # ── Backend ──────────────────────────────────────
    "Backend Developer":        ["Python", "MySQL", "Flask", "REST APIs"],
    "Backend Intern":           ["Python", "MySQL", "Flask"],
    "Java Backend Developer":   ["Java", "Spring Boot", "MySQL"],
    "API Developer":            ["Python", "REST APIs", "PostgreSQL"],
    "Node.js Developer":        ["JavaScript", "Node.js", "Express.js", "MongoDB"],

    # ── Frontend / Full Stack ─────────────────────────
    "Frontend Developer":       ["HTML", "CSS", "JavaScript", "React"],
    "Full Stack Developer":     ["Python", "React", "REST APIs", "MySQL"],
    "React Developer":          ["React", "JavaScript", "CSS", "HTML"],

    # ── Data ─────────────────────────────────────────
    "Data Analyst":             ["SQL", "Data Analysis", "Power BI", "Excel"],
    "Data Analyst Intern":      ["SQL", "Data Analysis"],
    "Data Scientist":           ["Python", "Machine Learning", "Pandas", "NumPy", "SQL"],
    "Data Scientist Intern":    ["Python", "Pandas", "Scikit-learn"],

    # ── ML / AI ──────────────────────────────────────
    "ML Engineer":              ["Python", "Machine Learning", "Scikit-learn", "AWS"],
    "ML Intern":                ["Python", "Machine Learning", "Scikit-learn"],
    "Deep Learning Engineer":   ["Python", "Deep Learning", "TensorFlow", "PyTorch"],
    "AI Engineer":              ["Python", "Machine Learning", "Deep Learning", "NLP"],
    "NLP Engineer":             ["Python", "NLP", "Hugging Face", "PyTorch"],
    "Computer Vision Engineer": ["Python", "Computer Vision", "OpenCV", "TensorFlow"],
    "LLM Engineer":             ["Python", "LangChain", "Hugging Face", "NLP"],

    # ── Cloud / DevOps ────────────────────────────────
    "Cloud Engineer":           ["AWS", "Docker", "Kubernetes"],
    "DevOps Engineer":          ["AWS", "Docker", "Git", "CI/CD", "Kubernetes"],
    "MLOps Engineer":           ["Python", "Docker", "AWS", "CI/CD", "Machine Learning"],
    "Site Reliability Engineer":["Linux", "Docker", "Kubernetes", "CI/CD", "AWS"],

    # ── Systems / Language-specific ───────────────────
    "Python Developer":         ["Python", "Git", "MySQL"],
    "C++ Developer":            ["C++", "Data Structures", "Algorithms"],
    "Go Developer":             ["Go", "REST APIs", "Docker"],

    # ── Generic Fallback Roles ────────────────────────
    "Software Engineer":        ["Data Structures", "Algorithms", "Git", "OOP"],
    "Systems Engineer":         ["Operating Systems", "Networking", "C++", "Linux"],
}


EXPERIENCE_VARIANTS = [
    ("Intern", 0),
    ("Junior", 1),
    ("Mid", 2),
    ("Senior", 3),
]


class Command(BaseCommand):
    help = "Seeds the database with an expanded set of Skills and Jobs (clears existing data first)"

    def handle(self, *args, **kwargs):
        self.stdout.write("🧹 Clearing existing data...")
        Job.objects.all().delete()
        Skill.objects.all().delete()

        self.stdout.write("🌱 Seeding skills...")
        skill_objects = {}
        for skill_name in SKILLS:
            obj, _ = Skill.objects.get_or_create(name=skill_name)
            skill_objects[skill_name] = obj

        self.stdout.write("🌱 Seeding jobs...")
        for base_title, skill_names in JOB_TEMPLATES.items():
            for level, min_exp in EXPERIENCE_VARIANTS:
                if "Intern" in base_title and level != "Intern":
                    continue
                if "Intern" not in base_title and level == "Intern":
                    continue

                title = f"{base_title} ({level})"
                job, _ = Job.objects.get_or_create(
                    title=title,
                    defaults={"min_experience": min_exp}
                )
                for skill_name in skill_names:
                    if skill_name in skill_objects:
                        job.skills.add(skill_objects[skill_name])

        self.stdout.write(self.style.SUCCESS(
            f"✅ Seeded {Skill.objects.count()} skills and {Job.objects.count()} jobs!"
        ))
