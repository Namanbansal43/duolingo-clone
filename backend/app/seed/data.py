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
DEFAULT_LEARNER_GEMS = 500

# key, title, description ({threshold} is filled in per tier), metric, thresholds for tiers 1, 2, 3...
ACHIEVEMENTS: list[tuple[str, str, str, str, tuple[int, ...]]] = [
    ("wildfire", "Wildfire", "Reach a {threshold} day streak", "streak", (3, 7, 14, 30)),
    ("sage", "Sage", "Earn {threshold} XP", "total_xp", (100, 250, 500, 1000)),
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
# (days before the first seed, lessons finished that day). Four lessons: all of "Say hello" and the
# first of "Introduce yourself", on three consecutive days ending yesterday.
DEMO_HISTORY: list[tuple[int, int]] = [(3, 2), (2, 1), (1, 1)]
