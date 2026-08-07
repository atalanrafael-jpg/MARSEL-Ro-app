from __future__ import annotations

import re
import sys
from pathlib import Path

from spellchecker import SpellChecker

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "README.md",
    ROOT / "README_GPT_INTEGRATION.md",
    ROOT / "API.md",
    ROOT / "SECURITY.md",
]

# Technical tokens and product/API names that should not be treated as Russian words.
ALLOWLIST = {
    "MARSEL", "RO", "App", "API", "GPT", "GitHub", "Actions", "HTTP", "JSON",
    "URL", "URLs", "README", "V20", "Python", "FastAPI", "pytest", "httpx",
    "OpenAI", "Bearer", "GET", "POST", "PUT", "PATCH", "DELETE", "readme",
}

CYRILLIC_WORD = re.compile(r"^[А-Яа-яЁё-]+$")


def markdown_text(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"!?(?:\[[^\]]*\])\([^)]*\)", " ", text)
    return text


def check_punctuation(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        if re.search(r"\s{2,}", line) and not line.lstrip().startswith(">"):
            errors.append(f"{path.relative_to(ROOT)}:{lineno}: repeated spaces")
        if re.search(r"\s+[,.!?;:]", line):
            errors.append(f"{path.relative_to(ROOT)}:{lineno}: space before punctuation")
        if re.search(r"[А-Яа-яЁё0-9][,.!?;:][А-Яа-яЁё]", line):
            errors.append(f"{path.relative_to(ROOT)}:{lineno}: missing space after punctuation")
        if re.search(r"[!?]{2,}", line):
            errors.append(f"{path.relative_to(ROOT)}:{lineno}: repeated !/? punctuation")
    return errors


def main() -> int:
    spell = SpellChecker(language="ru", distance=1)
    errors: list[str] = []
    checked = 0

    for path in TARGETS:
        if not path.exists():
            continue
        checked += 1
        raw = path.read_text(encoding="utf-8")
        text = markdown_text(raw)
        errors.extend(check_punctuation(path, text))
        words = re.findall(r"[А-Яа-яЁё-]+", text)
        candidates = {
            word.lower()
            for word in words
            if CYRILLIC_WORD.fullmatch(word) and word not in ALLOWLIST and len(word) > 2
        }
        unknown = sorted(spell.unknown(candidates))
        for word in unknown:
            errors.append(f"{path.relative_to(ROOT)}: possible spelling error: {word}")

    print("=== MARSEL LANGUAGE QUALITY CHECK ===")
    print(f"files_checked={checked}")
    print(f"issues_found={len(errors)}")
    if errors:
        for error in errors:
            print(error)
        print("LANGUAGE QUALITY RESULT: FAILED")
        print("Note: automated spelling checks are advisory; semantic/editorial proofreading still requires human review.")
        return 1

    print("LANGUAGE QUALITY RESULT: PASSED")
    print("Checked Russian spelling candidates and basic punctuation patterns.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
