from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("recommend-by-skills", views.recommend_by_skills, name="recommend_by_skills"),
    path("career-advice", views.career_advice, name="career_advice"),
    path("health/db", views.db_health, name="db_health"),
    path("parse-resume", views.parse_resume_view, name="parse_resume"),
    path("api/metrics", views.metrics, name="metrics"),
]
