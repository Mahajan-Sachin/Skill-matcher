import json
from django.test import TestCase, Client

from recommender.models import Skill, Job
from recommender.services.recommender import (
    normalize,
    normalize_title,
    get_from_fallback,
    get_recommendations_by_skills,
)


# ============================================================
#  MODEL TESTS
# ============================================================

class SkillModelTest(TestCase):
    """Tests for the Skill model."""

    def test_skill_creation_and_str(self):
        """Skill saves correctly and __str__ returns its name."""
        skill = Skill.objects.create(name="Python")
        self.assertEqual(skill.name, "Python")
        self.assertEqual(str(skill), "Python")

    def test_skill_name_is_unique(self):
        """Creating two skills with the same name should raise an error."""
        Skill.objects.create(name="Docker")
        with self.assertRaises(Exception):
            Skill.objects.create(name="Docker")


class JobModelTest(TestCase):
    """Tests for the Job model and its M2M relationship with Skill."""

    def setUp(self):
        self.py = Skill.objects.create(name="Python")
        self.sql = Skill.objects.create(name="SQL")
        self.job = Job.objects.create(title="Data Analyst", min_experience=1)
        self.job.skills.add(self.py, self.sql)

    def test_job_str(self):
        self.assertEqual(str(self.job), "Data Analyst")

    def test_job_min_experience(self):
        self.assertEqual(self.job.min_experience, 1)

    def test_job_skills_count(self):
        self.assertEqual(self.job.skills.count(), 2)

    def test_job_skills_names(self):
        names = set(self.job.skills.values_list("name", flat=True))
        self.assertIn("Python", names)
        self.assertIn("SQL", names)

    def test_job_can_exist_without_skills(self):
        """blank=True means a Job with no skills is valid."""
        empty_job = Job.objects.create(title="Empty Role", min_experience=0)
        self.assertEqual(empty_job.skills.count(), 0)


# ============================================================
#  RECOMMENDER SERVICE TESTS
# ============================================================

class NormalizeTest(TestCase):
    """Tests for the normalize() helper."""

    def test_lowercases_skills(self):
        self.assertEqual(normalize(["Python", "SQL"]), {"python", "sql"})

    def test_strips_whitespace(self):
        self.assertEqual(normalize(["  Python  ", " Docker "]), {"python", "docker"})

    def test_removes_empty_strings(self):
        self.assertEqual(normalize(["Python", "", "   "]), {"python"})


class NormalizeTitleTest(TestCase):
    """Tests for the normalize_title() helper."""

    def test_strips_experience_suffix(self):
        self.assertEqual(normalize_title("Data Scientist (Junior)"), "data scientist")
        self.assertEqual(normalize_title("ML Engineer (Senior)"), "ml engineer")

    def test_title_with_no_suffix(self):
        self.assertEqual(normalize_title("Backend Developer"), "backend developer")


class FallbackRecommenderTest(TestCase):
    """Tests for get_from_fallback() — no DB needed."""

    def test_python_matches_backend_intern(self):
        results = get_from_fallback({"python"}, experience=0)
        titles = [r["title"] for r in results]
        self.assertIn("Backend Intern", titles)

    def test_python_matches_ml_intern(self):
        results = get_from_fallback({"python"}, experience=0)
        titles = [r["title"] for r in results]
        self.assertIn("ML Intern", titles)

    def test_experience_filter_applied(self):
        """Jobs requiring more experience than user has should be excluded."""
        results = get_from_fallback({"python", "aws"}, experience=0)
        for r in results:
            self.assertEqual(r["min_experience"], 0)

    def test_no_match_returns_empty(self):
        results = get_from_fallback({"cobol"}, experience=5)
        self.assertEqual(results, [])

    def test_result_has_required_keys(self):
        results = get_from_fallback({"python"}, experience=0)
        self.assertGreater(len(results), 0)
        for r in results:
            self.assertIn("title", r)
            self.assertIn("score", r)
            self.assertIn("matched_skills", r)
            self.assertIn("missing_skills", r)

    def test_score_is_between_0_and_1(self):
        results = get_from_fallback({"python"}, experience=0)
        for r in results:
            self.assertGreaterEqual(r["score"], 0)
            self.assertLessEqual(r["score"], 1)


class GetRecommendationsTest(TestCase):
    """Tests for the main get_recommendations_by_skills() engine."""

    def test_results_sorted_by_score_descending(self):
        results = get_recommendations_by_skills(["Python", "Docker", "AWS"], experience=3)
        scores = [r["score"] for r in results]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_empty_skills_returns_empty(self):
        results = get_recommendations_by_skills([], experience=0)
        self.assertEqual(results, [])

    def test_unknown_skills_returns_empty(self):
        results = get_recommendations_by_skills(["cobol", "fortran"], experience=0)
        self.assertEqual(results, [])


# ============================================================
#  VIEW / API TESTS
# ============================================================

class IndexViewTest(TestCase):
    """Tests for the main page."""

    def test_index_returns_200(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_index_uses_correct_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "recommender/index.html")


class DbHealthViewTest(TestCase):
    """Tests for /health/db"""

    def test_returns_200(self):
        response = self.client.get("/health/db")
        self.assertEqual(response.status_code, 200)

    def test_returns_success_status(self):
        data = json.loads(self.client.get("/health/db").content)
        self.assertEqual(data["status"], "success")
        self.assertIn("db_latency_ms", data)


class MetricsViewTest(TestCase):
    """Tests for /api/metrics"""

    def test_returns_200(self):
        response = self.client.get("/api/metrics")
        self.assertEqual(response.status_code, 200)

    def test_response_structure(self):
        data = json.loads(self.client.get("/api/metrics").content)
        self.assertIn("database", data)
        self.assertIn("jobs_count", data["database"])
        self.assertIn("skills_count", data["database"])
        self.assertIn("ping_latency_ms", data["database"])

    def test_counts_reflect_db(self):
        """After seeding 2 skills and 1 job, metrics should match."""
        Skill.objects.create(name="Python")
        Skill.objects.create(name="SQL")
        job = Job.objects.create(title="Test Role", min_experience=0)

        data = json.loads(self.client.get("/api/metrics").content)
        self.assertEqual(data["database"]["skills_count"], 2)
        self.assertEqual(data["database"]["jobs_count"], 1)


class RecommendBySkillsViewTest(TestCase):
    """Tests for POST /recommend-by-skills"""

    def _post(self, payload):
        return self.client.post(
            "/recommend-by-skills",
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_valid_request_returns_200(self):
        response = self._post({"skills": "Python, Docker", "experience": 2})
        self.assertEqual(response.status_code, 200)

    def test_response_has_recommendations_and_meta(self):
        data = json.loads(self._post({"skills": "Python", "experience": 0}).content)
        self.assertIn("recommendations", data)
        self.assertIn("meta", data)
        self.assertIn("query_latency_ms", data["meta"])

    def test_invalid_json_returns_400(self):
        response = self.client.post(
            "/recommend-by-skills",
            data="not-valid-json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_get_method_not_allowed(self):
        response = self.client.get("/recommend-by-skills")
        self.assertEqual(response.status_code, 405)
