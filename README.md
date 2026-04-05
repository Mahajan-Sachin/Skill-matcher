# 🎯 SkillMatch — AI-Powered Skill Recommendation Engine

> **Django 6 · PostgreSQL · Groq LLM (Llama 3.1) · Dockerized**

A full-stack web application that recommends jobs based on your skills and years of experience. Upload your resume (PDF or Word) to auto-extract skills and calculate total experience across multiple employers.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📄 **Resume Parsing** | Upload PDF or Word — auto-extracts skills and calculates total experience |
| 🔍 **Job Recommendations** | Ranked matches by skill overlap score |
| 📊 **Skills Gap Analysis** | Shows matched skills ✅ AND what to learn next 📚 |
| ⚡ **Latency Tracking** | Every API response includes `query_latency_ms` + `X-Response-Time-ms` header |
| 📈 **Metrics Endpoint** | `/api/metrics` — DB ping latency, job count, skill count |
| 🤖 **AI Career Advisor** | Groq LLM (Llama 3.1) gives role-specific learning advice |
| 🛠️ **Django Admin** | Browse/edit all Jobs & Skills at `/admin` |
| 🐳 **Docker Ready** | Multi-stage `Dockerfile` + `docker-compose.yml` with PostgreSQL |

---

## 🚀 Quick Start (Local)

### Prerequisites
- Python 3.11+
- PostgreSQL running locally
- Groq API key (free at [console.groq.com](https://console.groq.com))

### 1. Clone & Install

```bash
git clone https://github.com/Mahajan-Sachin/Skill-matcher.git
cd Skill-matcher
pip install -r requirements.txt
```

### 2. Configure `.env`

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_NAME=skill_recommender
GROQ_API_KEY=your_groq_key_here
```

### 3. Setup Database

```bash
python manage.py migrate
python manage.py seed_db       # loads 65 skills + 76 job roles
python manage.py createsuperuser
```

### 4. Run

```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000**

---

## 🐳 Docker (One Command)

```bash
docker-compose up --build
```

This spins up PostgreSQL + Django, runs migrations, seeds data, and starts the server automatically.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Main UI |
| `POST` | `/parse-resume` | Upload PDF/Word → extract skills + experience |
| `POST` | `/recommend-by-skills` | `{skills, experience}` → ranked jobs with gap analysis |
| `POST` | `/career-advice` | `{role}` → Groq LLM career advice |
| `GET` | `/api/metrics` | DB latency, job/skill counts, system health |
| `GET` | `/health/db` | Database connection health check |
| `GET/POST` | `/admin/` | Django Admin panel |

### Sample Response — `/recommend-by-skills`

```json
{
  "recommendations": [
    {
      "title": "Data Scientist (Junior)",
      "score": 0.75,
      "matched_skills": ["python", "pandas", "scikit-learn"],
      "missing_skills": ["sql", "numpy"]
    }
  ],
  "meta": {
    "jobs_found": 26,
    "query_latency_ms": 107.72
  }
}
```

---

## 🏗️ Project Structure

```
skill-matcher/
├── manage.py
├── requirements.txt
├── Dockerfile                       # Multi-stage build
├── docker-compose.yml               # Django + PostgreSQL
│
├── config/                          # Django project config
│   ├── settings.py                  # PostgreSQL, middleware
│   ├── urls.py
│   └── wsgi.py
│
└── recommender/                     # Main app
    ├── models.py                    # Skill, Job (ORM)
    ├── views.py                     # All views + latency tracking
    ├── urls.py                      # 6 routes
    ├── admin.py                     # Django Admin
    ├── middleware.py                 # X-Response-Time-ms header
    ├── migrations/                  # Versioned schema
    ├── services/
    │   ├── recommender.py           # ORM engine + gap analysis
    │   ├── resume_parser.py         # PDF/Word → LLM → structured data
    │   └── fallback_data.py         # Static fallback if DB down
    ├── management/commands/
    │   └── seed_db.py               # python manage.py seed_db
    ├── templates/recommender/
    │   └── index.html
    └── static/recommender/
        └── style.css
```

---

## 🧠 Tech Stack

- **Backend:** Django 6.0.2, Python 3.11
- **Database:** PostgreSQL + Django ORM
- **AI/LLM:** Groq API (Llama 3.1-8b-instant)
- **PDF Parsing:** pdfplumber
- **Word Parsing:** python-docx
- **Containerization:** Docker, Docker Compose
- **Frontend:** Vanilla HTML/CSS/JS (dark mode, glassmorphism)

---

## 📸 Screenshots

> Resume upload with auto-extraction, skill gap analysis, and latency tracking

*Coming soon*

---

## 📄 License

MIT
