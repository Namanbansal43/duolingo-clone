"""The Spanish course (for English speakers): units, path nodes, lessons and the exercises in them.

Each unit follows the rhythm of Duolingo's path: two lesson nodes, a treasure chest, another lesson node,
then the unit review trophy. Unit 1 is playable: each of its 7 lessons has one exercise of every type.
Units 2 and 3 are on the path to show it continuing; their lessons have no exercises yet ("coming soon").

Option and tile order doesn't matter here: the API shuffles them for every session.
"""

from typing import NamedTuple

from app.models import SkillKind


class Choice(NamedTuple):
    """multiple_choice: pick the meaning of `prompt` (written in `language`)."""

    prompt: str
    language: str
    answer: str
    wrong: list[str]


class Tiles(NamedTuple):
    """word_bank: translate `prompt` by tapping tiles; `answers[0]` is the main translation."""

    prompt: str
    language: str
    answers: list[str]
    distractors: list[str]


class Pairs(NamedTuple):
    """match_pairs: (Spanish, English)."""

    pairs: list[tuple[str, str]]


class Blank(NamedTuple):
    """fill_blank: a Spanish sentence with ___ and the word that fills it."""

    prompt: str
    answer: str
    wrong: list[str]


class Typed(NamedTuple):
    """type_answer: translate `prompt` by typing; `answers[0]` is the main translation."""

    prompt: str
    language: str
    answers: list[str]


class Listen(NamedTuple):
    """listen: the Spanish sentence is read aloud and rebuilt from its words plus `distractors`."""

    sentence: str
    distractors: list[str]


ExerciseSeed = Choice | Tiles | Pairs | Blank | Typed | Listen


class SkillSeed(NamedTuple):
    title: str
    kind: SkillKind
    lessons: list[list[ExerciseSeed]]  # one list of exercises per lesson; empty lists are lessons to come


class UnitSeed(NamedTuple):
    title: str
    skills: list[SkillSeed]


def tile_words(sentence: str) -> list[str]:
    """The tiles a sentence is built from: its words without punctuation, "¿Cómo te llamas?" -> 3 tiles."""
    return [word.strip("¿¡?!.,") for word in sentence.split()]


SAY_HELLO = [
    [
        Choice("hello", "en", "hola", ["adiós", "gracias"]),
        Pairs([("hola", "hello"), ("adiós", "goodbye"), ("gracias", "thank you"), ("por favor", "please")]),
        Tiles("Hola, gracias.", "es", ["Hello, thank you.", "Hi, thank you."], ["please", "goodbye", "Hi"]),
        Blank("___, adiós.", "Gracias", ["Por", "Buenos"]),
        Typed("Adiós.", "es", ["Goodbye.", "Bye.", "Good bye."]),
        Listen("Gracias, adiós.", ["hola", "por"]),
    ],
    [
        Choice("buenas noches", "es", "good night", ["good morning", "please"]),
        Pairs(
            [
                ("buenos días", "good morning"),
                ("buenas noches", "good night"),
                ("sí", "yes"),
                ("de nada", "you're welcome"),
            ]
        ),
        Tiles("Good morning, thank you.", "en", ["Buenos días, gracias."], ["noches", "adiós"]),
        Blank("Buenos ___.", "días", ["noches", "gracias"]),
        Typed("Thank you.", "en", ["Gracias."]),
        Listen("Sí, gracias.", ["de", "nada"]),
    ],
]

INTRODUCE_YOURSELF = [
    [
        Choice("I", "en", "yo", ["sí", "soy"]),
        Pairs([("yo", "I"), ("soy", "I am"), ("me llamo", "my name is"), ("hola", "hello")]),
        Tiles("Soy Ana.", "es", ["I am Ana.", "I'm Ana."], ["Juan", "you", "my"]),
        Blank("Yo ___ Juan.", "soy", ["llamo", "gracias"]),
        Typed(
            "Me llamo Ana.",
            "es",
            ["My name is Ana.", "My name's Ana.", "I am called Ana.", "I'm called Ana."],
        ),
        Listen("Hola, soy Juan.", ["Ana", "yo"]),
    ],
    [
        Choice("mucho gusto", "es", "nice to meet you", ["good night", "thank you"]),
        Pairs(
            [
                ("mucho gusto", "nice to meet you"),
                ("¿y tú?", "and you?"),
                ("me llamo", "my name is"),
                ("adiós", "goodbye"),
            ]
        ),
        Tiles("What is your name?", "en", ["¿Cómo te llamas?"], ["soy", "yo"]),
        Blank("Me ___ Ana.", "llamo", ["soy", "gusto"]),
        Typed("Nice to meet you.", "en", ["Mucho gusto."]),
        Listen("Mucho gusto, Ana.", ["soy", "noches"]),
    ],
]

MEET_PEOPLE = [
    [
        Choice("she", "en", "ella", ["él", "yo"]),
        Pairs([("él", "he"), ("ella", "she"), ("amigo", "friend"), ("es", "is")]),
        Tiles("Él es mi amigo.", "es", ["He is my friend.", "He's my friend."], ["she", "I", "your"]),
        Blank("Ella ___ Ana.", "es", ["soy", "llamo"]),
        Typed("She is my friend.", "en", ["Ella es mi amiga."]),
        Listen("Ella es mi amiga.", ["amigo", "él"]),
    ],
    [
        Choice("niño", "es", "boy", ["girl", "man"]),
        Pairs([("hombre", "man"), ("mujer", "woman"), ("niño", "boy"), ("niña", "girl")]),
        Tiles("The woman is Ana.", "en", ["La mujer es Ana."], ["hombre", "El"]),
        Blank("El ___ es Juan.", "hombre", ["mujer", "niña"]),
        Typed("Él es un niño.", "es", ["He is a boy.", "He's a boy."]),
        Listen("La niña es Ana.", ["niño", "El"]),
    ],
]

UNIT_ONE_REVIEW = [
    [
        Choice("thank you", "en", "gracias", ["de nada", "por favor"]),
        Pairs(
            [
                ("hola", "hello"),
                ("adiós", "goodbye"),
                ("ella", "she"),
                ("mucho gusto", "nice to meet you"),
                ("niño", "boy"),
            ]
        ),
        Tiles(
            "Hola, me llamo Ana.",
            "es",
            ["Hello, my name is Ana.", "Hi, my name is Ana."],
            ["she", "you", "Hi"],
        ),
        Blank("Buenas ___, Juan.", "noches", ["días", "gusto"]),
        Typed(
            "Goodbye, my friend.",
            "en",
            ["Adiós, mi amigo.", "Adiós, amigo.", "Adiós, mi amiga.", "Adiós, amiga."],
        ),
        Listen("Buenos días, soy Ana.", ["noches", "él"]),
    ],
]

COMING_SOON: list[list[ExerciseSeed]] = [[], []]  # two lessons without content yet


def _unit(title: str, lessons: tuple[list, list, list, list] | None, names: tuple[str, str, str]) -> UnitSeed:
    first, second, third, review = lessons or (COMING_SOON, COMING_SOON, COMING_SOON, [[]])
    return UnitSeed(
        title,
        [
            SkillSeed(names[0], SkillKind.LESSON, first),
            SkillSeed(names[1], SkillKind.LESSON, second),
            SkillSeed("Treasure chest", SkillKind.CHEST, []),
            SkillSeed(names[2], SkillKind.LESSON, third),
            SkillSeed("Unit review", SkillKind.REVIEW, review),
        ],
    )


UNITS: list[UnitSeed] = [
    _unit(
        "Greet people and introduce yourself",
        (SAY_HELLO, INTRODUCE_YOURSELF, MEET_PEOPLE, UNIT_ONE_REVIEW),
        ("Say hello", "Introduce yourself", "Meet people"),
    ),
    _unit("Order food and drink", None, ("Drinks", "Food", "At the café")),
    _unit("Get around town", None, ("Places", "Directions", "Transport")),
]
