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

ALLOWLIST = {
    "MARSEL", "RO", "App", "API", "GPT", "GitHub", "Actions", "HTTP", "JSON",
    "URL", "URLs", "README", "V20", "Python", "FastAPI", "pytest", "httpx",
    "OpenAI", "Bearer", "GET", "POST", "PUT", "PATCH", "DELETE", "readme",
}

CYRILLIC_WORD = re.compile(r"^[А-Яа-яЁё]+$")


def markdown_text(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"!?(?:\[[^\]]*\])\([^)]*\)", " ", text)
    return text


def check_punctuation(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        # Two trailing spaces are valid Markdown hard line breaks.
        meaningful = line.rstrip()
        if re.search(r"\s{2,}", meaningful) and not meaningful.lstrip().startswith(">"):
            errors.append(f"{path.relative_to(ROOT)}:{lineno}: repeated internal spaces")
        if re.search(r"\s+[,.!?;:]", meaningful):
            errors.append(f"{path.relative_to(ROOT)}:{lineno}: space before punctuation")
        if re.search(r"[А-Яа-яЁё0-9][,.!?;:][А-Яа-яЁё]", meaningful):
            errors.append(f"{path.relative_to(ROOT)}:{lineno}: missing space after punctuation")
        if re.search(r"[!?]{2,}", meaningful):
            errors.append(f"{path.relative_to(ROOT)}:{lineno}: repeated !/? punctuation")
    return errors


def spelling_advisories(path: Path, text: str, spell: SpellChecker) -> list[str]:
    # pyspellchecker is advisory: inflected Russian forms and technical terms
    # can legitimately be absent from its dictionary. Hyphenated words are
    # checked by their individual Cyrillic components.
    words = re.findall(r"[А-Яа-яЁё]+", text)
    allow = {x.lower() for x in ALLOWLIST}
    candidates = {
        word.lower()
        for word in words
        if CYRILLIC_WORD.fullmatch(word) and word.lower() not in allow and len(word) > 2
    }
    return [
        f"{path.relative_to(ROOT)}: spelling advisory: {word}"
        for word in sorted(spell.unknown(candidates))
    ]


def main() -> int:
    spell = SpellChecker(language="ru", distance=1)
    punctuation_errors: list[str] = []
    spelling_notes: list[str] = []
    checked = 0

    for path in TARGETS:
        if not path.exists():
            continue
        checked += 1
        raw = path.read_text(encoding="utf-8")
        text = markdown_text(raw)
        punctuation_errors.extend(check_punctuation(path, text))
        spelling_notes.extend(spelling_advisories(path, text, spell))

    print("=== MARSEL LANGUAGE QUALITY CHECK ===")
    print(f"files_checked={checked}")
    print(f"punctuation_issues={len(punctuation_errors)}")
    print(f"spelling_advisories={len(spelling_notes)}")

    for error in punctuation_errors:
        print(error)
    for note in spelling_notes:
        print(note)

    if punctuation_errors:
        print("LANGUAGE QUALITY RESULT: FAILED")
        print("Spelling advisories are non-blocking; punctuation findings are blocking.")
        return 1

    print("LANGUAGE QUALITY RESULT: PASSED")
    print("No blocking punctuation defects detected. Spelling output is advisory and requires editorial review for context.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
