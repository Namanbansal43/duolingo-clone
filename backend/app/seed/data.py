"""Seed content, kept apart from the seeding logic so it reads as plain data."""

# (code, title) for courses taught in English, in duolingo.com's order. Only Spanish has content.
COURSES: list[tuple[str, str]] = [
    ("es", "Spanish"),
    ("fr", "French"),
    ("de", "German"),
    ("it", "Italian"),
    ("pt", "Portuguese"),
    ("nl", "Dutch"),
    ("ja", "Japanese"),
    ("ar", "Arabic"),
    ("cs", "Czech"),
    ("cy", "Welsh"),
    ("da", "Danish"),
    ("el", "Greek"),
    ("eo", "Esperanto"),
    ("fi", "Finnish"),
    ("ga", "Irish"),
    ("gd", "Scottish Gaelic"),
    ("he", "Hebrew"),
    ("hi", "Hindi"),
    ("ht", "Haitian Creole"),
    ("hu", "Hungarian"),
    ("hv", "High Valyrian"),
    ("haw", "Hawaiian"),
    ("id", "Indonesian"),
    ("ko", "Korean"),
    ("la", "Latin"),
    ("nb", "Norwegian (Bokmål)"),
    ("nv", "Navajo"),
    ("pl", "Polish"),
    ("ro", "Romanian"),
    ("ru", "Russian"),
    ("sv", "Swedish"),
    ("sw", "Swahili"),
    ("tlh", "Klingon"),
    ("tr", "Turkish"),
    ("uk", "Ukrainian"),
    ("vi", "Vietnamese"),
    ("yi", "Yiddish"),
    ("zh", "Chinese (Simplified)"),
    ("zu", "Zulu"),
]
AVAILABLE_COURSES = {"es"}

# The built-in learner. Their username comes from settings (DEFAULT_USERNAME).
DEFAULT_LEARNER_NAME = "Alex"
DEFAULT_LEARNER_COURSE = "es"
DEFAULT_LEARNER_DAILY_GOAL_XP = 20

# key, title, description ({threshold} is filled in per tier), metric, thresholds for tiers 1, 2, 3...
# Wildfire and Sage have duolingo.com's ten levels; Scholar counts lessons here rather than words.
ACHIEVEMENTS: list[tuple[str, str, str, str, tuple[int, ...]]] = [
    (
        "wildfire",
        "Wildfire",
        "Reach a {threshold} day streak",
        "streak",
        (3, 7, 14, 30, 50, 75, 125, 180, 250, 365),
    ),
    (
        "sage",
        "Sage",
        "Earn {threshold} XP",
        "total_xp",
        (100, 250, 500, 1000, 2000, 3000, 5000, 10000, 20000, 30000),
    ),
    ("scholar", "Scholar", "Complete {threshold} lessons", "lessons_completed", (5, 10, 25, 50)),
    (
        "sharpshooter",
        "Sharpshooter",
        "Complete {threshold} lessons without a mistake",
        "perfect_lessons",
        (3, 10, 25, 50),
    ),
]

# The built-in learner starts with a little history so the path, streak and XP have something to show:
# (days before the first seed, lessons finished that day). Three lessons: both of "Say hello" and the
# first of "Introduce yourself", on three consecutive days ending yesterday.
DEMO_HISTORY: list[tuple[int, int]] = [(3, 1), (2, 1), (1, 1)]

# The ten leagues, lowest first: name, how many move up, how many move down at the end of a week.
LEAGUES: list[tuple[str, int, int]] = [
    ("Bronze", 7, 0),
    ("Silver", 7, 5),
    ("Gold", 7, 5),
    ("Sapphire", 7, 5),
    ("Ruby", 7, 5),
    ("Emerald", 7, 5),
    ("Amethyst", 7, 5),
    ("Pearl", 7, 5),
    ("Obsidian", 7, 5),
    ("Diamond", 0, 5),
]

# Rivals in the learner's league (29, so a league has 30 members as on duolingo.com): display name, XP on a
# day they practise, days a week they practise. From a few keen learners down to occasional ones.
RIVALS: list[tuple[str, int, int]] = [
    ("Sofía", 55, 6),
    ("Kenji", 50, 5),
    ("Amara", 45, 5),
    ("Lukas", 40, 5),
    ("Priya", 40, 4),
    ("Mateo", 35, 4),
    ("Chloé", 30, 4),
    ("Yusuf", 30, 4),
    ("Hana", 25, 4),
    ("Diego", 25, 3),
    ("Olivia", 25, 3),
    ("Arjun", 20, 3),
    ("Fatima", 20, 3),
    ("Noah", 20, 3),
    ("Ingrid", 15, 3),
    ("Tomás", 15, 3),
    ("Mei", 15, 2),
    ("Kwame", 15, 2),
    ("Elif", 10, 3),
    ("Luca", 10, 2),
    ("Zara", 10, 2),
    ("Ravi", 10, 2),
    ("Nadia", 10, 1),
    ("Jonas", 10, 1),
    ("Camila", 10, 1),
    ("Ahmed", 10, 1),
    ("Freya", 10, 1),
    ("Hiroshi", 10, 1),
    ("Ana", 10, 1),
]
