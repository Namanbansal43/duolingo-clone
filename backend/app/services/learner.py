from datetime import date, datetime, timedelta

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import (
    Course,
    LeagueMembership,
    LessonSession,
    SessionStatus,
    User,
    UserAchievement,
    UserSettings,
    UserSkillProgress,
    XpEvent,
)
from app.schemas.me import MeUpdate, Onboarding
from app.schemas.settings import UserSettingsUpdate
from app.services.hearts import live_hearts
from app.services.rules import HEART_REFILL_GEMS, STARTING_GEMS

# The choices on the settings page. They belong to the device more than to the progress, so they carry over
# from one learner to the next ("Get started", resetting the demo).
PREFERENCES = ("sound_effects", "animations", "motivational_messages", "listening_exercises", "dark_mode")
GUEST_NAME = "Guest"


def available_course(db: Session, course_id: int) -> Course:
    """The course with this id, if learners can study it; otherwise a 404 or 409 error."""
    course = db.get(Course, course_id)
    if course is None:
        raise AppError(404, "course_not_found", "That course does not exist.")
    if not course.is_available:
        raise AppError(409, "course_unavailable", f"{course.title} is coming soon.")
    return course


def update_learner(db: Session, user: User, changes: MeUpdate) -> None:
    """Apply the learner's own preferences (course, daily goal, time zone). Omitted fields are unchanged."""
    if changes.active_course_id is not None:
        user.active_course = available_course(db, changes.active_course_id)

    if changes.daily_goal_xp is not None:
        user.daily_goal_xp = changes.daily_goal_xp

    if changes.timezone is not None:
        user.timezone = changes.timezone

    db.commit()


def learner_settings(db: Session, user: User) -> UserSettings:
    """The learner's preferences, created with the defaults the first time they are needed."""
    if user.settings is None:
        user.settings = UserSettings()
        db.flush()
    return user.settings


def update_settings(db: Session, user: User, changes: UserSettingsUpdate) -> UserSettings:
    """Save the choices made on the settings page. Omitted fields are unchanged."""
    settings = learner_settings(db, user)
    for name, value in changes.model_dump(exclude_none=True).items():
        setattr(settings, name, value)
    db.commit()
    return settings


def preferences(db: Session, user: User) -> dict[str, object]:
    """The learner's choices on the settings page, to carry over to another learner."""
    settings = learner_settings(db, user)
    return {name: getattr(settings, name) for name in PREFERENCES}


def set_preferences(db: Session, user: User, values: dict[str, object]) -> None:
    settings = learner_settings(db, user)
    for name, value in values.items():
        setattr(settings, name, value)


def start_as_new_learner(
    db: Session, username: str, current: User, choices: Onboarding, now: datetime
) -> User:
    """Finish "Get started": a brand-new guest (no profile yet) begins at the first node of the chosen
    course. The guest is its own learner, separate from the demo learner, so the demo's progress is never
    touched. There is one guest: the first "Get started" creates it, later ones clear its history (lesson
    sessions and their answers, XP, path progress, achievements) and reset its stats. The current
    learner's preferences on the settings page carry over. Nothing changes if the course can't be
    studied."""
    course = available_course(db, choices.active_course_id)

    user = db.scalar(select(User).where(User.username == username))
    if user is None:
        user = User(username=username, display_name=GUEST_NAME, hearts_updated_at=now, created_at=now)
        db.add(user)
        db.flush()
    for model in (XpEvent, LessonSession, UserSkillProgress, UserAchievement, LeagueMembership):
        db.execute(delete(model).where(model.user_id == user.id))  # answers go with their sessions
    if user is not current:
        set_preferences(db, user, preferences(db, current))

    user.created_at = now
    user.is_guest = True
    user.active_course = course
    user.daily_goal_xp = choices.daily_goal_xp
    user.timezone = choices.timezone
    user.total_xp = 0
    user.gems = STARTING_GEMS
    user.hearts = user.max_hearts
    user.hearts_updated_at = now
    user.current_streak = user.longest_streak = 0
    user.last_streak_date = None
    user.streak_freezes = 0
    db.commit()
    return user


def refill_hearts(db: Session, user: User, now: datetime, regen_every: timedelta) -> None:
    """Buy a full set of hearts with gems."""
    if live_hearts(user, now, regen_every).current >= user.max_hearts:
        raise AppError(409, "hearts_full", "Your hearts are already full.")
    if user.gems < HEART_REFILL_GEMS:
        raise AppError(409, "not_enough_gems", f"Refilling hearts costs {HEART_REFILL_GEMS} gems.")
    user.gems -= HEART_REFILL_GEMS
    user.hearts = user.max_hearts
    user.hearts_updated_at = now
    db.commit()


def xp_earned_on(db: Session, user: User, day: date) -> int:
    """XP earned on one of the learner's calendar days (the daily goal compares against this)."""
    total = db.scalar(
        select(func.sum(XpEvent.amount)).where(XpEvent.user_id == user.id, XpEvent.local_date == day)
    )
    return total or 0


def daily_xp(db: Session, user: User, last_day: date, days: int) -> list[tuple[date, int]]:
    """XP per calendar day for the `days` days ending on `last_day`, oldest first, days without XP
    included."""
    first_day = last_day - timedelta(days=days - 1)
    totals = {
        day: xp
        for day, xp in db.execute(
            select(XpEvent.local_date, func.sum(XpEvent.amount))
            .where(XpEvent.user_id == user.id, XpEvent.local_date.between(first_day, last_day))
            .group_by(XpEvent.local_date)
        )
    }
    return [
        (day, totals.get(day, 0)) for day in (first_day + timedelta(days=offset) for offset in range(days))
    ]


def lessons_completed(db: Session, user: User, *, perfect: bool = False) -> int:
    """Lessons and practice sessions finished; with `perfect`, only those without a mistake."""
    query = (
        select(func.count())
        .select_from(LessonSession)
        .where(LessonSession.user_id == user.id, LessonSession.status == SessionStatus.COMPLETED)
    )
    if perfect:
        query = query.where(LessonSession.mistakes == 0)
    return db.scalar(query)
