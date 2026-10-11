"""ResumeLens entry point / user interface.

Usage:
    python main.py data/resumes/wednesday_addams.txt
    python main.py data/resumes/*.txt --format html --out data/output
    python main.py                       (processes every file in data/resumes)
    python main.py --validate resumelens/dsl/examples/invalid/lexical_bad_email.rlp
"""
import argparse
import sys
from pathlib import Path

from resumelens.dsl.parser import validate
from resumelens.pipeline import process_file, write_outputs

DEFAULT_INPUT = Path("data/resumes")
DEFAULT_OUTPUT = Path("data/output")


def show(path, result, verbose):
    print(f"\n=== {Path(path).name} ===")
    print(f"Candidate: {result.extracted['name'] or 'unknown'}")
    print(f"[1] extracted  : {', '.join(result.extracted['raw_skills']) or '-'}")
    print(f"[2] normalized : {', '.join(result.normalized) or '-'}")
    if result.unknown:
        print(f"    unknown    : {', '.join(result.unknown)}")
    print("[3] recognition:")
    for r in result.recognitions:
        line = f"    {r.title:27} {r.result:9}"
        if verbose:
            line += " " + " -> ".join(r.trace)
        elif r.accepted:
            line += " " + " ".join(r.word)
        elif r.missing_blocks:
            line += " missing " + ", ".join(r.missing_blocks)
        print(line)
    status = "valid" if result.valid else f"INVALID: {result.error}"
    print(f"[4] profile    : {status}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="ResumeLens: formal language-based résumé screening")
    parser.add_argument("files", nargs="*", help="résumé .txt files (default: every file in data/resumes)")
    parser.add_argument("--format", choices=["html", "md", "both"], default="both",
                        help="visualization to generate (default: both)")
    parser.add_argument("--out", default=str(DEFAULT_OUTPUT), help="output directory (default: data/output)")
    parser.add_argument("--trace", action="store_true", help="print the state trace of every automaton")
    parser.add_argument("--validate", metavar="PROFILE", nargs="+",
                        help="only validate existing .rlp candidate profiles")
    args = parser.parse_args(argv)

    if args.validate:
        failures = 0
        for path in args.validate:
            ok, error = validate(Path(path).read_text(encoding="utf-8"))
            print(f"{path}: {'VALID' if ok else error}")
            failures += not ok
        return 1 if failures else 0

    files = [Path(f) for f in args.files] or sorted(DEFAULT_INPUT.glob("*.txt"))
    if not files:
        print("No résumés to process.", file=sys.stderr)
        return 1

    formats = ("html", "md") if args.format == "both" else (args.format,)
    for path in files:
        result = process_file(path)
        show(path, result, args.trace)
        written = write_outputs(result, args.out, path.stem, formats)
        print("    written    : " + ", ".join(str(p) for p in written))
    return 0


if __name__ == "__main__":
    sys.exit(main())
