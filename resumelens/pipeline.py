"""Full ResumeLens pipeline: résumé text -> validated candidate profile.

    Stage 1  extraction.extract            regular expressions
    Stage 2  normalization + canonical order finite-state transducers
    Stage 3  recognition.recognize_all     finite automata
    Stage 4  dsl generator + parser        context-free grammar (textX)
             render                        HTML / Markdown
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from resumelens.dsl.generator import to_dsl
from resumelens.dsl.parser import ProfileError, parse
from resumelens.extraction import extract, save_json
from resumelens.normalization import normalize_skills_safe
from resumelens.recognition import Recognition, recognize_all
from resumelens.render import to_html, to_markdown
from resumelens.sorting import canonical_orders


@dataclass
class PipelineResult:
    extracted: Dict
    normalized: List[str]
    unknown: List[str]
    orders: Dict[str, List[str]]
    recognitions: List[Recognition]
    profile_text: str
    error: Optional[str] = None
    model: object = field(default=None, repr=False)

    @property
    def valid(self) -> bool:
        return self.error is None

    @property
    def accepted(self) -> List[str]:
        return [r.title for r in self.recognitions if r.accepted]


def process_text(text: str) -> PipelineResult:
    extracted = extract(text)                                   # Stage 1
    normalized, unknown = normalize_skills_safe(extracted["raw_skills"])  # Stage 2
    normalized = list(dict.fromkeys(normalized))
    orders = canonical_orders(normalized)
    recognitions = recognize_all(normalized)                    # Stage 3
    profile_text = to_dsl(extracted, normalized, recognitions)  # Stage 4
    result = PipelineResult(extracted, normalized, unknown, orders, recognitions, profile_text)
    try:
        result.model = parse(profile_text)
    except ProfileError as err:
        result.error = str(err)
    return result


def process_file(path) -> PipelineResult:
    return process_text(Path(path).read_text(encoding="utf-8"))


def write_outputs(result: PipelineResult, out_dir, stem: str, formats=("html", "md")) -> List[Path]:
    """
    Writes <stem>.json (Stage 1 data), <stem>.rlp (candidate profile) and,
    if the profile is valid, the requested visualizations.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = [out / f"{stem}.json", out / f"{stem}.rlp"]
    save_json(result.extracted, paths[0])
    paths[1].write_text(result.profile_text, encoding="utf-8")
    if result.valid:
        for fmt in formats:
            path = out / f"{stem}.{fmt}"
            path.write_text(to_html(result.model) if fmt == "html" else to_markdown(result.model),
                            encoding="utf-8")
            paths.append(path)
    return paths
