import json
import re
import sys
from pathlib import Path

NAME = re.compile(r"\A\s*([A-ZÁÉÍÓÚÑ][\w'-]+(?:[ \t]+[A-ZÁÉÍÓÚÑ][\w'-]+){1,3})[ \t]*$", re.M)
EMAIL = r"[\w.%+-]+@[\w-]+(?:\.[\w-]+)+"
PHONE = r"(?<!\d)(?:\+\d{1,3}[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}(?!\d)"
LINKEDIN = r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+"
GITHUB = r"(?:https?://)?(?:www\.)?github\.com/[\w-]+"
EXPERIENCE = re.compile(r"(\d+)\+?\s*years?\s+of\s+experience\s*(?:in|as|with)?\s*([^.\n]*)", re.I)
EDUCATION = re.compile(
    r"\b(B\.?Sc\.?|M\.?Sc\.?|Ph\.?D\.?|Bachelor's|Bachelor|Master's|Master)(?![a-z])"
    r"[ \t]*(?:in|of)?[ \t]*([^.\n]*)", re.I)

SKILLS = {
    "database": r"postgres(?:ql)?|my[\s-]?sql|sql[\s-]?server|sqlite|mongo(?:[\s-]?db)?|redis|oracle|no[\s-]?sql",
    "framework_library": r"react(?:\.?js)?|angular(?:\.?js)?|vue(?:\.?js)?|next\.?js|node(?:\.?js)?"
                         r"|express(?:\.?js)?|django|flask|fast[\s-]?api|spring(?:[\s-]?boot)?|pandas"
                         r"|num[\s-]?py|scikit[\s-]?learn|sk[\s-]?learn|tensor[\s-]?flow|py[\s-]?torch"
                         r"|keras|matplotlib|py[\s-]?spark|spark",
    "tool_technology": r"git[\s-]?hub|git[\s-]?lab|git|docker|kubernetes|k8s|aws|azure|gcp"
                       r"|rest(?:ful)?(?:\s+apis?)?|graph[\s-]?ql|jenkins|airflow|power[\s-]?bi|tableau"
                       r"|excel|jupyter|linux",
    "competency": r"machine[\s-]?learning(?:\s+models?)?|ml|deep[\s-]?learning|predictive\s+models?"
                  r"|data[\s-]?processing(?:\s+pipelines?)?|web\s+applications?|ci/cd",
    "programming_language": r"java[\s-]?script|js|type[\s-]?script|ts|python(?:\s?3)?|py|java|c#|c\+\+"
                            r"|kotlin|golang|go(?=\s*[,.;\n])|sql",
}
TECHNICAL = ("programming_language", "framework_library", "database", "tool_technology")

LEFT, RIGHT = r"(?<![\w#+.])", r"(?![\w#+])"

SKIP = "|".join([EMAIL, LINKEDIN, GITHUB, r"https?://\S+"])
SCANNER = re.compile(
    f"(?P<skip>{SKIP})|" + "|".join(f"(?P<{cat}>{LEFT}(?:{p}){RIGHT})" for cat, p in SKILLS.items()),
    re.I)


def _unique(items):
    """Drop case-insensitive duplicates, keeping the first spelling and order."""
    seen = {}
    for item in items:
        seen.setdefault(item.lower(), item)
    return list(seen.values())


def _skills(text):
    """(category, string) pairs, in order, never overlapping (finditer resumes after each match)."""
    return [(m.lastgroup, m.group()) for m in SCANNER.finditer(text) if m.lastgroup != "skip"]


def extract_name(text):
    m = NAME.search(text)
    return m.group(1) if m else None


def extract_contact(text):
    return {key: _unique(re.findall(rx, text, re.I))
            for key, rx in [("emails", EMAIL), ("phones", PHONE), ("linkedin", LINKEDIN), ("github", GITHUB)]}


def extract_experience(text):
    return [{"years": int(y), "description": d.strip()} for y, d in EXPERIENCE.findall(text)]


def extract_education(text):
    return [{"degree": deg, "field": field.strip()} for deg, field in EDUCATION.findall(text)]


def extract_qualifications(text):
    found = _skills(text)
    return {cat: _unique(s for c, s in found if c == cat) for cat in SKILLS}


def extract(text):
    """Stage 1 output. 'raw_skills' (order of appearance) is the input to Stage 2."""
    return {
        "name": extract_name(text),
        "contact": extract_contact(text),
        "experience": extract_experience(text),
        "education": extract_education(text),
        "qualifications": extract_qualifications(text),
        "raw_skills": _unique(s for c, s in _skills(text) if c in TECHNICAL),
    }


def extract_file(path):
    return extract(Path(path).read_text(encoding="utf-8"))


def save_json(data, path):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    print(json.dumps(extract_file(sys.argv[1]), indent=2, ensure_ascii=False))
