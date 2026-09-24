"""Vergleicht einen FalconEYE-JSON-Report mit den erwarteten Findings.

Ablauf:
    falconeye scan tests/fixtures --format json --output report.json --force-reindex
    python scripts/evaluate_fixtures.py report.json

Ein Finding gilt als Treffer, wenn es in der richtigen Datei liegt und seine
Zeilen die erwartete Zeile +/- `tolerance` abdecken. Ob auch die Kategorie
stimmt, wird zusätzlich über Stichwörter im Issue-Text geprüft.

Findings in Dateien ohne erwartete Findings sind Fehlalarme. Zusätzliche
Findings in verwundbaren Dateien werden separat als "unerwartet" gelistet,
weil sie auch berechtigt sein können.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import yaml

DEFAULT_FIXTURES = Path(__file__).resolve().parent.parent / "tests" / "fixtures"

CATEGORY_KEYWORDS = {
    "sql": ["sql"],
    "command": ["command", "shell", "exec", "system(", "process"],
    "code_exec": ["eval", "code injection", "code exec", "arbitrary code"],
    "deserialization": ["deserializ", "pickle", "unserialize", "yaml", "marshal"],
    "xss": ["xss", "cross-site scripting", "html injection", "innerhtml"],
    "path": ["path traversal", "directory traversal", "file inclusion", "lfi", "path"],
    "ssrf": ["ssrf", "server-side request", "request forgery"],
    "redirect": ["redirect"],
    "secret": ["secret", "hardcoded", "hard-coded", "credential", "api key", "apikey"],
    "xxe": ["xxe", "external entit", "xml"],
    "weak_crypto": ["md5", "sha1", "weak hash", "weak crypt", "password hash", "insecure hash"],
    "tls": ["certificate", "tls", "ssl", "man-in-the-middle", "mitm"],
    "prototype_pollution": ["prototype pollution", "__proto__", "prototype"],
    "format_string": ["format string"],
    "buffer_overflow": ["buffer overflow", "overflow", "out-of-bounds", "bounds", "strcpy", "memcpy"],
    "integer_overflow": ["integer overflow", "overflow", "wrap"],
    "use_after_free": ["use-after-free", "use after free", "dangling", "freed"],
}


@dataclass
class Expected:
    file: str
    line: int
    category: str
    contains: str
    matched_by: dict | None = None
    category_ok: bool = False


@dataclass
class FileResult:
    file: str
    language: str
    expected: list[Expected] = field(default_factory=list)
    unexpected: list[dict] = field(default_factory=list)

    @property
    def is_safe(self) -> bool:
        return not self.expected


def load_expected(fixtures: Path) -> tuple[int, dict[str, FileResult]]:
    data = yaml.safe_load((fixtures / "expected.yaml").read_text(encoding="utf-8"))
    results = {}
    for entry in data["files"]:
        fr = FileResult(entry["file"], entry["language"])
        fr.expected = [Expected(entry["file"], f["line"], f["category"], f["contains"])
                       for f in entry["findings"]]
        results[entry["file"]] = fr
    return data.get("tolerance", 3), results


def fixture_for(path: str, known: dict[str, FileResult]) -> str | None:
    norm = path.replace("\\", "/")
    for rel in known:
        if norm == rel or norm.endswith("/" + rel):
            return rel
    return None


def category_matches(category: str, finding: dict) -> bool:
    text = " ".join(str(finding.get(k, "")) for k in ("issue", "reasoning")).lower()
    return any(k in text for k in CATEGORY_KEYWORDS.get(category, [category]))


def evaluate(report: dict, fixtures: Path) -> tuple[dict[str, FileResult], list[dict]]:
    tolerance, results = load_expected(fixtures)
    outside = []
    for finding in report.get("findings", []):
        loc = finding.get("location", {})
        rel = fixture_for(loc.get("file_path") or "", results)
        if rel is None:
            outside.append(finding)
            continue
        fr = results[rel]
        start = loc.get("line_start") or 0
        end = loc.get("line_end") or start
        candidates = [e for e in fr.expected
                      if e.matched_by is None and start - tolerance <= e.line <= end + tolerance]
        # Bevorzugt eine Erwartung, deren Kategorie zum Issue-Text passt
        candidates.sort(key=lambda e: (not category_matches(e.category, finding), abs(e.line - start)))
        if candidates:
            e = candidates[0]
            e.matched_by = finding
            e.category_ok = category_matches(e.category, finding)
        else:
            fr.unexpected.append(finding)
    return results, outside


def summarize(results: dict[str, FileResult]) -> dict:
    expected = [e for fr in results.values() for e in fr.expected]
    hits = [e for e in expected if e.matched_by]
    fps = sum(len(fr.unexpected) for fr in results.values() if fr.is_safe)
    extra = sum(len(fr.unexpected) for fr in results.values() if not fr.is_safe)
    recall = len(hits) / len(expected) if expected else 1.0
    precision = len(hits) / (len(hits) + fps) if hits or fps else 1.0
    return {
        "expected": len(expected), "found": len(hits),
        "category_ok": sum(1 for e in hits if e.category_ok),
        "false_positives": fps, "unexpected_in_vulnerable": extra,
        "recall": round(recall, 3), "precision_safe_files": round(precision, 3),
    }


def print_report(results: dict[str, FileResult], outside: list[dict]) -> None:
    by_lang: dict[str, list[FileResult]] = defaultdict(list)
    for fr in results.values():
        by_lang[fr.language].append(fr)

    print(f"{'Sprache':<12} {'Gefunden':>9} {'Kategorie ok':>13} {'Fehlalarme':>11} {'Unerwartet':>11}")
    print("-" * 60)
    for lang in sorted(by_lang):
        frs = by_lang[lang]
        exp = [e for fr in frs for e in fr.expected]
        hits = [e for e in exp if e.matched_by]
        fps = sum(len(fr.unexpected) for fr in frs if fr.is_safe)
        extra = sum(len(fr.unexpected) for fr in frs if not fr.is_safe)
        print(f"{lang:<12} {len(hits):>4}/{len(exp):<4} {sum(e.category_ok for e in hits):>13} {fps:>11} {extra:>11}")

    missed = [e for fr in results.values() for e in fr.expected if not e.matched_by]
    if missed:
        print("\nNicht gefunden:")
        for e in missed:
            print(f"  {e.file}:{e.line}  [{e.category}]  {e.contains}")

    wrong_cat = [e for fr in results.values() for e in fr.expected if e.matched_by and not e.category_ok]
    if wrong_cat:
        print("\nRichtige Stelle, aber andere Kategorie im Issue-Text:")
        for e in wrong_cat:
            print(f"  {e.file}:{e.line}  erwartet [{e.category}], gemeldet: {e.matched_by.get('issue', '')[:70]}")

    fps = [(fr.file, f) for fr in results.values() if fr.is_safe for f in fr.unexpected]
    if fps:
        print("\nFehlalarme (Findings in sicheren Dateien):")
        for file, f in fps:
            print(f"  {file}:{f['location'].get('line_start')}  {f.get('issue', '')[:80]}")

    extra = [(fr.file, f) for fr in results.values() if not fr.is_safe for f in fr.unexpected]
    if extra:
        print("\nUnerwartete Findings in verwundbaren Dateien (manuell prüfen):")
        for file, f in extra:
            print(f"  {file}:{f['location'].get('line_start')}  {f.get('issue', '')[:80]}")

    if outside:
        print(f"\n{len(outside)} Findings außerhalb der Testdateien wurden ignoriert.")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("report", help="FalconEYE-Report im JSON-Format")
    ap.add_argument("--fixtures", default=str(DEFAULT_FIXTURES))
    ap.add_argument("--min-recall", type=float, default=None, help="Exit-Code 1, wenn darunter")
    ap.add_argument("--max-false-positives", type=int, default=None, help="Exit-Code 1, wenn darüber")
    ap.add_argument("--json", action="store_true", help="nur Kennzahlen als JSON ausgeben")
    args = ap.parse_args(argv)

    report = json.loads(Path(args.report).read_text(encoding="utf-8"))
    results, outside = evaluate(report, Path(args.fixtures))
    summary = summarize(results)

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print_report(results, outside)
        print("\n" + "=" * 60)
        print(f"Trefferquote (Recall):     {summary['found']}/{summary['expected']}  = {summary['recall']:.0%}")
        print(f"Kategorie korrekt:         {summary['category_ok']}/{summary['found']}")
        print(f"Fehlalarme (sichere Dat.): {summary['false_positives']}")
        print(f"Präzision (sichere Dat.):  {summary['precision_safe_files']:.0%}")
        print(f"Unerwartet (verw. Dat.):   {summary['unexpected_in_vulnerable']}")

    failed = ((args.min_recall is not None and summary["recall"] < args.min_recall)
              or (args.max_false_positives is not None and summary["false_positives"] > args.max_false_positives))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
