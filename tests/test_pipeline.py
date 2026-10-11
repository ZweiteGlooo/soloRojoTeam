"""End-to-end tests: résumé text -> Stage 1 -> 2 -> 3 -> 4."""
import pytest

import main
from resumelens.dsl.parser import validate
from resumelens.pipeline import process_file, process_text, write_outputs

EXPECTED = {
    "wednesday_addams": ["Full Stack Developer"],
    "mary_jane_watson": ["Machine Learning Engineer"],
    "peter_parker": ["Full Stack Developer", "Backend Developer"],
}


@pytest.mark.parametrize("name,profiles", EXPECTED.items())
def test_sample_resumes(name, profiles):
    result = process_file(f"data/resumes/{name}.txt")
    assert result.valid, result.error
    assert result.accepted == profiles


def test_stages_are_connected():
    result = process_file("data/resumes/wednesday_addams.txt")
    assert result.extracted["raw_skills"] == ["JS", "React.js", "NodeJS", "Postgres", "Git"]
    assert result.normalized == ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]
    assert result.orders["FULL_STACK_DEVELOPER"] == ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]
    assert [r.result for r in result.recognitions] == ["ACCEPTED", "REJECTED", "REJECTED", "REJECTED"]
    assert result.model.name == "Wednesday Addams"


def test_statement_ml_example():
    text = """Lucas Sinclair
lucas@hawkins.edu
Technical Skills: Git, Postgres, TensorFlow, Pandas, Python."""
    result = process_text(text)
    assert result.orders["MACHINE_LEARNING_ENGINEER"] == ["PYTHON", "PANDAS", "TENSORFLOW", "POSTGRESQL", "GIT"]
    assert result.accepted == ["Machine Learning Engineer"]


def test_order_in_resume_does_not_change_the_result():
    a = process_text("Ana Ruiz\nSkills: JS, React, Node.js, MySQL, Git")
    b = process_text("Ana Ruiz\nSkills: Git, MySQL, Node.js, React, JS")
    assert a.accepted == b.accepted == ["Full Stack Developer"]


def test_data_engineer_resume():
    text = """Robin Buckley
robin@scoops.com | +1 555 123 4567
5 years of experience building ETL pipelines.
Skills: Python, Spark, Airflow, Kafka, PostgreSQL, AWS, Docker, Git."""
    result = process_text(text)
    assert result.accepted == ["Data Engineer"]
    assert result.model.experience.jobs[0].years == 5


def test_resume_without_skills_is_still_a_valid_profile():
    result = process_text("Steve Harrington\nI am good with people.")
    assert result.valid
    assert result.accepted == []
    assert result.model.skills.items == []


def test_unknown_skills_are_reported_not_fatal():
    result = process_text("Eddie Munson\nSkills: Python, Pandas, Excel")
    assert "PYTHON" in result.normalized
    assert result.valid


def test_write_outputs(tmp_path):
    result = process_file("data/resumes/peter_parker.txt")
    paths = write_outputs(result, tmp_path, "peter", ("html", "md"))
    assert [p.name for p in paths] == ["peter.json", "peter.rlp", "peter.html", "peter.md"]
    assert validate((tmp_path / "peter.rlp").read_text(encoding="utf-8"))[0]
    assert "Backend Developer" in (tmp_path / "peter.html").read_text(encoding="utf-8")


class TestCommandLine:
    def test_process_one_file(self, tmp_path, capsys):
        code = main.main(["data/resumes/mary_jane_watson.txt", "--out", str(tmp_path), "--format", "md"])
        out = capsys.readouterr().out
        assert code == 0
        assert "Machine Learning Engineer   ACCEPTED" in out
        assert (tmp_path / "mary_jane_watson.md").exists()
        assert not (tmp_path / "mary_jane_watson.html").exists()

    def test_trace(self, tmp_path, capsys):
        main.main(["data/resumes/wednesday_addams.txt", "--out", str(tmp_path), "--trace"])
        assert "q0 -> LANGUAGE -> FRONTEND -> BACKEND -> DATABASE -> VCS" in capsys.readouterr().out

    def test_validate_mode(self, capsys):
        code = main.main(["--validate", "resumelens/dsl/examples/valid/wednesday_addams.rlp",
                          "resumelens/dsl/examples/invalid/syntax_missing_skills.rlp"])
        out = capsys.readouterr().out
        assert code == 1
        assert "wednesday_addams.rlp: VALID" in out
        assert "Expected 'skills'" in out
