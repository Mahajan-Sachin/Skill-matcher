from django.contrib import admin
from .models import Skill, Job


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    search_fields = ["name"]


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "min_experience"]
    list_filter = ["min_experience"]
    search_fields = ["title"]
    filter_horizontal = ["skills"]
