"""Tests for the extraction stage (Stage 1 — regular expressions)."""

from pathlib import Path

from resumelens.extraction import (
    extract, extract_contact, extract_name, extract_experience,
    extract_education, extract_qualifications,
)

RESUMES = Path(__file__).parent.parent / "data" / "resumes"
WEDNESDAY = (RESUMES / "wednesday_addams.txt").read_text(encoding="utf-8")
MARY_JANE = (RESUMES / "mary_jane_watson.txt").read_text(encoding="utf-8")


# --- reference examples from the assignment --------------------------------

def test_wednesday_raw_skills_match_assignment_example():
    assert extract(WEDNESDAY)["raw_skills"] == ["JS", "React.js", "NodeJS", "Postgres", "Git"]


def test_mary_jane_raw_skills():
    assert extract(MARY_JANE)["raw_skills"] == [
        "Python", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "SQL", "Git"]


# --- candidate data --------------------------------------------------------

def test_name_is_first_line():
    assert extract_name(WEDNESDAY) == "Wednesday Addams"
    assert extract_name(MARY_JANE) == "Mary Jane Watson"


def test_name_absent_when_first_line_is_not_a_name():
    assert extract_name("technical skills: python") is None


def test_contact_information():
    text = "mail: ana.p@uni.edu.co | +57 300 123 4567 | linkedin.com/in/ana-p | https://github.com/anap"
    c = extract_contact(text)
    assert c["emails"] == ["ana.p@uni.edu.co"]
    assert c["phones"] == ["+57 300 123 4567"]
    assert c["linkedin"] == ["linkedin.com/in/ana-p"]
    assert c["github"] == ["https://github.com/anap"]


def test_experience_years_and_description():
    assert extract_experience(WEDNESDAY) == [
        {"years": 3, "description": "developing web applications"}]


def test_education_degrees():
    edu = extract_education("B.Sc. in Software Engineering.\nMaster's in Data Science.")
    assert [e["degree"] for e in edu] == ["B.Sc.", "Master's"]
    assert edu[0]["field"] == "Software Engineering"


# --- qualifications: spelling variants, boundaries, overlaps ---------------

def test_spelling_variants_are_kept_as_written():
    q = extract_qualifications("Skills: Javascript, scikit learn, Py Torch, Tensor Flow")
    assert q["programming_language"] == ["Javascript"]
    assert q["framework_library"] == ["scikit learn", "Py Torch", "Tensor Flow"]


def test_java_is_not_found_inside_javascript():
    q = extract_qualifications("JavaScript")
    assert q["programming_language"] == ["JavaScript"]


def test_js_suffix_is_not_extracted_separately():
    assert extract("React.js, Node.js")["raw_skills"] == ["React.js", "Node.js"]


def test_git_is_not_found_inside_github():
    assert extract("GitHub")["raw_skills"] == ["GitHub"]


def test_longest_match_wins_on_overlap():
    # "SQL" inside "No SQL" must not be reported twice
    assert extract("No SQL")["raw_skills"] == ["No SQL"]


def test_no_false_positives_inside_words():
    # "rest" in "restaurant", "go" in "good", "ts" in "results"
    assert extract("Good results at the restaurant.")["raw_skills"] == []


def test_duplicates_removed_case_insensitive():
    assert extract("Python, python, PYTHON")["raw_skills"] == ["Python"]


def test_urls_and_emails_are_not_skills():
    text = "github.com/js-dev | node@python.org\nSkills: Git"
    assert extract(text)["raw_skills"] == ["Git"]
