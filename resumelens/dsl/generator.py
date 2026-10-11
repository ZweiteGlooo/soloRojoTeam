"""Write the candidate profile (DSL text) from the output of Stages 1-3."""
from pathlib import Path
from typing import Dict, List

from resumelens.recognition import Recognition


def _string(value) -> str:
    # STRING terminal is double quoted; keep the text simple instead of escaping
    return '"' + str(value).replace('"', "'").strip() + '"'


def _join(items) -> str:
    return ", ".join(items)


def to_dsl(extracted: Dict, normalized_skills: List[str], recognitions: List[Recognition]) -> str:
    """
    extracted: Stage 1 dict (extraction.extract)
    normalized_skills: Stage 2 output
    recognitions: Stage 3 output (recognition.recognize_all)
    """
    lines = [f"candidate {_string(extracted.get('name') or 'Unknown candidate')} {{"]

    contact = extracted.get("contact", {})
    items = [f"email {e}" for e in contact.get("emails", [])]
    items += [f"phone {p}" for p in contact.get("phones", [])]
    items += [f"linkedin {u}" for u in contact.get("linkedin", [])]
    items += [f"github {u}" for u in contact.get("github", [])]
    if items:
        lines += ["    contact {"] + [f"        {i}" for i in items] + ["    }"]

    degrees = extracted.get("education", [])
    if degrees:
        lines.append("    education {")
        for d in degrees:
            field = f" in {_string(d['field'])}" if d.get("field") else ""
            lines.append(f"        degree {_string(d['degree'])}{field}")
        lines.append("    }")

    jobs = [j for j in extracted.get("experience", []) if j.get("years")]
    if jobs:
        lines.append("    experience {")
        for j in jobs:
            unit = "year" if j["years"] == 1 else "years"
            lines.append(f"        {j['years']} {unit} {_string(j.get('description') or 'experience')}")
        lines.append("    }")

    skills = list(dict.fromkeys(normalized_skills))
    lines.append(f"    skills {{ {_join(skills)} }}" if skills else "    skills { }")

    lines.append("    profiles {")
    for r in recognitions:
        if r.accepted:
            lines.append(f"        {r.profile}: ACCEPTED [{_join(r.word)}]")
        elif r.missing_blocks:
            lines.append(f"        {r.profile}: REJECTED missing [{_join(r.missing_blocks)}]")
        else:
            lines.append(f"        {r.profile}: REJECTED")
    lines += ["    }", "}"]
    return "\n".join(lines) + "\n"


def save_dsl(text: str, path) -> None:
    Path(path).write_text(text, encoding="utf-8")
