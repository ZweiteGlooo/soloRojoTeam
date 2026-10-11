"""Stage 4 — HTML/Markdown visualization of a validated candidate profile.

Only profiles accepted by the grammar are rendered: render() parses the DSL
text first, so an invalid profile raises ProfileError and nothing is produced.
"""
from html import escape
from pathlib import Path

from resumelens.dsl.parser import parse
from resumelens.patterns import get_pattern

CONTACT_LABELS = {"email": "Email", "phone": "Phone", "linkedin": "LinkedIn", "github": "GitHub"}


def _title(profile_key):
    return get_pattern(profile_key).title


def _link(item):
    if item.kind == "email":
        return f"mailto:{item.value}"
    if item.kind in ("linkedin", "github"):
        return item.value if item.value.startswith("http") else f"https://{item.value}"
    return None


def _accepted(model):
    return [r for r in model.profiles.results if r.status == "ACCEPTED"]


# ---------------------------------------------------------------------------
# Markdown
# ---------------------------------------------------------------------------

def to_markdown(model) -> str:
    out = [f"# {model.name}", ""]
    accepted = _accepted(model)
    out.append("**Accepted profiles:** " + (", ".join(_title(r.profile) for r in accepted) or "none"))
    out.append("")

    if model.contact:
        out += ["## Contact", ""]
        for item in model.contact.items:
            link = _link(item)
            value = f"[{item.value}]({link})" if link else item.value
            out.append(f"- **{CONTACT_LABELS[item.kind]}:** {value}")
        out.append("")

    if model.education:
        out += ["## Education", ""]
        out += [f"- {d.title}" + (f" in {d.field}" if d.field else "") for d in model.education.records]
        out.append("")

    if model.experience:
        out += ["## Experience", ""]
        out += [f"- {j.years} year{'s' if j.years != 1 else ''}: {j.description}" for j in model.experience.jobs]
        out.append("")

    out += ["## Skills", "", " · ".join(f"`{s}`" for s in model.skills.items) or "_none recognized_", ""]

    out += ["## Profile recognition", "", "| Profile | Result | Detail |", "|---|---|---|"]
    for r in model.profiles.results:
        if r.status == "ACCEPTED":
            detail = " ".join(r.word)
        else:
            detail = ("missing " + ", ".join(r.missing)) if r.missing else ""
        out.append(f"| {_title(r.profile)} | {'✅' if r.status == 'ACCEPTED' else '❌'} {r.status} | {detail} |")
    out.append("")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------

STYLE = """
  body { font-family: system-ui, -apple-system, "Segoe UI", sans-serif; background: #f4f5f7;
         color: #1f2328; margin: 0; padding: 32px 16px; }
  .card { max-width: 760px; margin: 0 auto; background: #fff; border-radius: 12px;
          box-shadow: 0 1px 4px rgba(0,0,0,.08); padding: 28px 32px; }
  h1 { margin: 0 0 4px; font-size: 28px; }
  h2 { font-size: 15px; text-transform: uppercase; letter-spacing: .06em; color: #57606a;
       margin: 28px 0 10px; border-bottom: 1px solid #eaeef2; padding-bottom: 6px; }
  .summary { color: #57606a; margin: 0; }
  ul { margin: 0; padding-left: 20px; } li { margin: 4px 0; }
  a { color: #0969da; text-decoration: none; }
  .chip { display: inline-block; background: #eef1f4; border-radius: 999px; padding: 3px 10px;
          margin: 3px 4px 3px 0; font-size: 13px; font-family: ui-monospace, Consolas, monospace; }
  table { width: 100%; border-collapse: collapse; font-size: 14px; }
  td, th { text-align: left; padding: 8px 6px; border-bottom: 1px solid #eaeef2; vertical-align: top; }
  .badge { font-weight: 600; font-size: 12px; padding: 2px 8px; border-radius: 6px; }
  .accepted { background: #dafbe1; color: #1a7f37; }
  .rejected { background: #ffebe9; color: #cf222e; }
  .word { font-family: ui-monospace, Consolas, monospace; font-size: 12px; color: #57606a; }
  footer { margin-top: 24px; font-size: 12px; color: #8c959f; }
"""


def to_html(model) -> str:
    e = escape
    accepted = _accepted(model)
    parts = [f"<h1>{e(model.name)}</h1>",
             '<p class="summary">Accepted profiles: '
             + (e(", ".join(_title(r.profile) for r in accepted)) or "none") + "</p>"]

    if model.contact:
        items = []
        for item in model.contact.items:
            link = _link(item)
            value = f'<a href="{e(link)}">{e(item.value)}</a>' if link else e(item.value)
            items.append(f"<li><strong>{CONTACT_LABELS[item.kind]}:</strong> {value}</li>")
        parts += ["<h2>Contact</h2>", "<ul>" + "".join(items) + "</ul>"]

    if model.education:
        items = [f"<li>{e(d.title)}" + (f" in {e(d.field)}" if d.field else "") + "</li>"
                 for d in model.education.records]
        parts += ["<h2>Education</h2>", "<ul>" + "".join(items) + "</ul>"]

    if model.experience:
        items = [f"<li><strong>{j.years} year{'s' if j.years != 1 else ''}</strong> {e(j.description)}</li>"
                 for j in model.experience.jobs]
        parts += ["<h2>Experience</h2>", "<ul>" + "".join(items) + "</ul>"]

    chips = "".join(f'<span class="chip">{e(s)}</span>' for s in model.skills.items)
    parts += ["<h2>Skills</h2>", f"<div>{chips or 'none recognized'}</div>"]

    rows = []
    for r in model.profiles.results:
        css = r.status.lower()
        if r.status == "ACCEPTED":
            detail = f'<span class="word">{e(" ".join(r.word))}</span>'
        else:
            detail = ("missing " + e(", ".join(r.missing))) if r.missing else ""
        rows.append(f"<tr><td>{e(_title(r.profile))}</td>"
                    f'<td><span class="badge {css}">{r.status}</span></td><td>{detail}</td></tr>')
    parts += ["<h2>Profile recognition</h2>",
              "<table><tr><th>Profile</th><th>Result</th><th>Recognized word / missing blocks</th></tr>"
              + "".join(rows) + "</table>"]

    body = "\n    ".join(parts)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(model.name)} · ResumeLens</title>
  <style>{STYLE}</style>
</head>
<body>
  <div class="card">
    {body}
    <footer>Generated by ResumeLens from a validated candidate profile.</footer>
  </div>
</body>
</html>
"""


# ---------------------------------------------------------------------------

def render(profile_text: str, fmt: str = "html") -> str:
    """Validate the DSL text and return its HTML or Markdown visualization."""
    model = parse(profile_text)
    if fmt == "html":
        return to_html(model)
    if fmt in ("md", "markdown"):
        return to_markdown(model)
    raise ValueError(f"Unknown format: {fmt}")


def render_file(profile_path, out_path, fmt: str = "html") -> Path:
    out = Path(out_path)
    out.write_text(render(Path(profile_path).read_text(encoding="utf-8"), fmt), encoding="utf-8")
    return out
