import re
import json
import os
from datetime import datetime, date

from groq import Groq


# =====================
# PDF TEXT EXTRACTION
# =====================

def extract_text_from_pdf(file):
    """Extract raw text from a PDF file object."""
    import pdfplumber
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


# =====================
# WORD TEXT EXTRACTION
# =====================

def extract_text_from_docx(file):
    """Extract raw text from a Word (.docx) file object."""
    from docx import Document
    doc = Document(file)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs).strip()


# =====================
# LLM PARSING
# =====================

def parse_with_llm(resume_text: str) -> dict:
    """
    Send resume text to Groq LLM.
    Returns dict with: skills (list) + experience (list of {company, start, end}).
    """
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        return {"error": "Groq API key not configured."}

    client = Groq(api_key=groq_key)

    prompt = f"""You are a resume parser. Extract data from the resume below.

Return ONLY valid JSON — no explanation, no markdown, no extra text.

Use exactly this structure:
{{
  "skills": ["Python", "Django", "SQL"],
  "experience": [
    {{"company": "Google", "start": "2018-02", "end": "2023-07"}},
    {{"company": "Amazon", "start": "2024-08", "end": "present"}}
  ]
}}

Rules:
- skills: only technical skills (languages, frameworks, tools, databases, cloud, etc.)
- start/end dates: YYYY-MM format only
- Use "present" if the job is current or ongoing
- If no date found for a job, skip that entry

RESUME:
{resume_text[:3500]}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=700,
        )
        content = response.choices[0].message.content.strip()

        # Pull JSON block even if LLM adds extra text
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())

        return {"error": "LLM did not return valid JSON."}

    except json.JSONDecodeError:
        return {"error": "Failed to parse LLM JSON response."}
    except Exception as e:
        return {"error": str(e)}


# =====================
# EXPERIENCE CALCULATION
# =====================

def calculate_total_experience(experience_periods: list) -> dict:
    """
    Sum up experience across all companies.

    Example:
      Google  2018-02 → 2023-07  =  5y 5m
      Amazon  2024-08 → present  =  ~10m
      Total   ≈ 6.3 years → 6 years (int for the form)
    """
    total_days = 0
    today = date.today()
    breakdown = []

    for period in experience_periods:
        company = period.get("company", "Unknown")
        start_str = period.get("start", "")
        end_str = str(period.get("end", "present")).strip().lower()

        try:
            start = datetime.strptime(start_str, "%Y-%m").date()

            if end_str in ("present", "current", "now", "ongoing", "till date", "till now"):
                end = today
            else:
                end = datetime.strptime(end_str, "%Y-%m").date()

            if end <= start:
                continue

            days = (end - start).days
            years = round(days / 365.25, 1)
            total_days += days

            breakdown.append({
                "company": company,
                "start": start_str,
                "end": end_str if end_str != str(today)[:7].lower() else "present",
                "years": years,
            })

        except Exception:
            # Skip entries with unparseable dates
            continue

    total_years_exact = round(total_days / 365.25, 1)
    total_years_int = int(total_years_exact)  # for auto-filling the form

    return {
        "total_years_exact": total_years_exact,
        "total_years_int": total_years_int,
        "breakdown": breakdown,
    }


# =====================
# MAIN PIPELINE
# =====================

def parse_resume(file, filename=""):
    """Full pipeline: PDF or Word file → skills + calculated experience."""
    try:
        fname = filename.lower()
        if fname.endswith(".docx"):
            text = extract_text_from_docx(file)
        elif fname.endswith(".pdf"):
            text = extract_text_from_pdf(file)
        else:
            return {"error": "Unsupported file type. Upload a PDF or Word (.docx) file."}

        if not text:
            return {"error": "Could not extract text from file. Make sure it's not a scanned image PDF."}

        parsed = parse_with_llm(text)
        if "error" in parsed:
            return parsed

        skills = parsed.get("skills", [])
        experience_periods = parsed.get("experience", [])

        exp_data = calculate_total_experience(experience_periods)

        return {
            "skills": skills,
            "skills_string": ", ".join(skills),
            "experience_years": exp_data["total_years_int"],
            "experience_years_exact": exp_data["total_years_exact"],
            "experience_breakdown": exp_data["breakdown"],
        }

    except Exception as e:
        return {"error": f"Resume parsing failed: {str(e)}"}
