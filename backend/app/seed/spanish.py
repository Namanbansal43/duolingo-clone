"""The Spanish course (for English speakers): units, their path nodes, and how many lessons each node has.

Each unit follows the same rhythm as Duolingo's path: two lesson nodes, a treasure chest, another lesson
node, then the unit review trophy. Exercises are added per lesson when the lesson player is built.
"""

from typing import NamedTuple

from app.models import SkillKind


class SkillSeed(NamedTuple):
    title: str
    kind: SkillKind
    lessons: int


class UnitSeed(NamedTuple):
    title: str
    skills: list[SkillSeed]


def _unit(title: str, first: str, second: str, third: str) -> UnitSeed:
    return UnitSeed(
        title,
        [
            SkillSeed(first, SkillKind.LESSON, 3),
            SkillSeed(second, SkillKind.LESSON, 3),
            SkillSeed("Treasure chest", SkillKind.CHEST, 0),
            SkillSeed(third, SkillKind.LESSON, 3),
            SkillSeed("Unit review", SkillKind.REVIEW, 2),
        ],
    )


UNITS: list[UnitSeed] = [
    _unit("Greet people and introduce yourself", "Say hello", "Introduce yourself", "Meet people"),
    _unit("Order food and drink", "Drinks", "Food", "At the café"),
    _unit("Get around town", "Places", "Directions", "Transport"),
]
