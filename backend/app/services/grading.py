"""How a written or tapped answer is compared with the accepted ones."""

import re
import unicodedata
from dataclasses import dataclass
from enum import StrEnum


class Verdict(StrEnum):
    CORRECT = "correct"
    OTHER_SOLUTION = "other_solution"  # right, but not the main translation, which is shown as well
    TYPO = "typo"  # right apart from one slip or a missing accent; the spelling is shown
    WRONG = "wrong"


@dataclass(frozen=True)
class Grade:
    verdict: Verdict
    solution: str | None  # what the feedback bar shows under its heading; None when there is nothing to add

    @property
    def correct(self) -> bool:
        return self.verdict != Verdict.WRONG


def normalize(text: str) -> str:
    """Case, punctuation (including ¿ and ¡) and spacing never make an answer wrong."""
    text = unicodedata.normalize("NFC", text).casefold().replace("\u2019", "'")  # curly apostrophe
    text = re.sub(r"[^\w\s']", " ", text)
    return " ".join(text.split())


def grade_text(answer: str, accepted: list[str], primary: str, *, lenient: bool) -> Grade:
    """Grade an answer against every accepted one (`primary` among them).

    `lenient` is for typed answers: a missing accent or a single wrong, missing or extra letter still
    counts, flagged as a typo. Answers built from tiles can't have typos, so they are graded strictly.
    """
    given = normalize(answer)
    for text in accepted:
        if normalize(text) == given:
            return Grade(Verdict.CORRECT, None) if text == primary else Grade(Verdict.OTHER_SOLUTION, primary)
    if lenient:
        plain_given = _strip_accents(given)
        for text in accepted:
            plain = _strip_accents(normalize(text))
            if plain == plain_given or (len(plain) >= 4 and _one_edit_apart(plain, plain_given)):
                return Grade(Verdict.TYPO, text)
    return Grade(Verdict.WRONG, primary)


def _strip_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text) if not unicodedata.combining(c))


def _one_edit_apart(a: str, b: str) -> bool:
    """True when b is a with exactly one letter changed, added or removed."""
    if abs(len(a) - len(b)) > 1 or a == b:
        return False
    if len(a) > len(b):
        a, b = b, a
    i = 0
    while i < len(a) and a[i] == b[i]:
        i += 1
    if len(a) == len(b):
        return a[i + 1 :] == b[i + 1 :]
    return a[i:] == b[i + 1 :]
