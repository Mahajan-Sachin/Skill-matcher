from django.db import models


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Job(models.Model):
    title = models.CharField(max_length=150)
    min_experience = models.IntegerField(default=0)
    skills = models.ManyToManyField(Skill, related_name="jobs", blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["title"]
