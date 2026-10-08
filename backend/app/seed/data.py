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
