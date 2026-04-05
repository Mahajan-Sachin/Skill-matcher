import json
import os
import time

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from groq import Groq
from .services.recommender import get_recommendations_by_skills
from .services.resume_parser import parse_resume
from django.db import connection


def index(request):
    return render(request, "recommender/index.html")


@csrf_exempt
@require_http_methods(["POST"])
def recommend_by_skills(request):
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    skills_input = data.get("skills", "")
    experience = int(data.get("experience", 0))
    user_skills = [s.strip() for s in skills_input.split(",") if s.strip()]

    t_start = time.perf_counter()
    try:
        recommendations = get_recommendations_by_skills(user_skills, experience)
    except Exception as e:
        return JsonResponse({"error": "Recommendation service failed.", "details": str(e)}, status=500)
    query_ms = round((time.perf_counter() - t_start) * 1000, 2)

    return JsonResponse({
        "input_skills": user_skills,
        "experience": experience,
        "recommendations": recommendations,
        "meta": {
            "jobs_found": len(recommendations),
            "query_latency_ms": query_ms,
        },
    })


@csrf_exempt
@require_http_methods(["POST"])
def career_advice(request):
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    role = data.get("role", "")
    custom_role = data.get("custom_role", "")
    final_role = custom_role.strip() if role == "OTHER" else role

    if not final_role:
        return JsonResponse({"error": "Role not provided."}, status=400)

    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        return JsonResponse({"error": "Groq API key not configured."}, status=200)

    client = Groq(api_key=groq_key)

    prompt = f"""You are a career advisor.

Explain for the role: {final_role}

1. Core technical skills required
2. Nice-to-have skills
3. Beginner learning focus
4. Common mistakes candidates make

Keep the response concise and structured."""

    t_start = time.perf_counter()
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=400,
        )
        llm_ms = round((time.perf_counter() - t_start) * 1000, 2)
        return JsonResponse({
            "advice": response.choices[0].message.content,
            "meta": {"llm_latency_ms": llm_ms},
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def db_health(request):
    try:
        t_start = time.perf_counter()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_ms = round((time.perf_counter() - t_start) * 1000, 2)
        return JsonResponse({
            "status": "success",
            "message": "Database connection successful",
            "db_latency_ms": db_ms,
        })
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


def metrics(request):
    """
    System metrics endpoint — DB latency, model counts, health status.
    Shows interviewers you understand observability and system monitoring.
    """
    from recommender.models import Job, Skill

    # DB ping latency
    t_start = time.perf_counter()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_ms = round((time.perf_counter() - t_start) * 1000, 2)
        db_status = "healthy"
    except Exception as e:
        db_ms = None
        db_status = str(e)

    # Model counts
    try:
        jobs_count = Job.objects.count()
        skills_count = Skill.objects.count()
    except Exception:
        jobs_count = skills_count = 0

    return JsonResponse({
        "status": db_status,
        "database": {
            "ping_latency_ms": db_ms,
            "jobs_count": jobs_count,
            "skills_count": skills_count,
        },
        "api_version": "1.0",
        "framework": "Django 6.0.2",
    })


@csrf_exempt
@require_http_methods(["POST"])
def parse_resume_view(request):
    if "resume" not in request.FILES:
        return JsonResponse({"error": "No file uploaded."}, status=400)

    file = request.FILES["resume"]
    fname = file.name.lower()

    if not (fname.endswith(".pdf") or fname.endswith(".docx")):
        return JsonResponse({"error": "Only PDF or Word (.docx) files are supported."}, status=400)

    t_start = time.perf_counter()
    result = parse_resume(file, filename=file.name)
    parse_ms = round((time.perf_counter() - t_start) * 1000, 2)

    if "error" in result:
        return JsonResponse(result, status=400)

    result["meta"] = {"parse_latency_ms": parse_ms}
    return JsonResponse(result)
