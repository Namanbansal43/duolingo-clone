import unicodedata
from datetime import UTC, datetime, time, timedelta
from typing import assert_never

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    AcceptedAnswer,
    Achievement,
    AchievementTier,
    Course,
    Exercise,
    ExerciseOption,
    ExerciseType,
    League,
    LeagueMembership,
    Lesson,
    LessonSession,
    Rival,
    SessionMode,
    SessionStatus,
    Skill,
    Unit,
    User,
    UserSettings,
    UserSkillProgress,
    XpEvent,
    XpSource,
)
from app.seed import data, spanish
from app.services.achievements import unlock_achievements
from app.services.leagues import week_start_of
from app.services.rules import LESSON_XP, STARTING_GEMS
from app.services.streak import local_date


def seed_database(db: Session, *, default_username: str, now: datetime) -> None:
    """Insert whatever seed data is missing. Safe to run on every start: existing rows,
    including the learner's progress, are never overwritten."""
    _seed_courses(db)
    _seed_spanish_content(db)
    _seed_achievements(db)
    _seed_leagues(db)
    _seed_rivals(db, now)
    learner = _seed_default_learner(db, default_username, now)
    # Award the levels the learner's progress already reaches: the demo history earns the first levels
    # of Wildfire (a 3 day streak) and Sharpshooter (3 lessons without a mistake).
    unlock_achievements(db, learner, now)
    db.commit()


def _seed_courses(db: Session) -> None:
    existing = set(db.scalars(select(Course.learning_language).where(Course.from_language == "en")))
    for position, (code, title) in enumerate(data.COURSES):
        if code not in existing:
            db.add(
                Course(
                    learning_language=code,
                    from_language="en",
                    title=title,
                    position=position,
                    is_available=code in data.AVAILABLE_COURSES,
                )
            )
    db.flush()


def _seed_spanish_content(db: Session) -> None:
    """Units, path nodes, lessons and exercises, matched by position so reruns only add what is missing.
    A lesson's exercises are only added while it has none, so seeded content is never rewritten."""
    course = db.scalars(
        select(Course).where(Course.learning_language == "es", Course.from_language == "en")
    ).one()
    units = {unit.position: unit for unit in course.units}
    for unit_position, unit_seed in enumerate(spanish.UNITS, start=1):
        unit = units.get(unit_position)
        if unit is None:
            unit = Unit(position=unit_position, title=unit_seed.title)
            course.units.append(unit)
        skills = {skill.position: skill for skill in unit.skills}
        for skill_position, skill_seed in enumerate(unit_seed.skills, start=1):
            skill = skills.get(skill_position)
            if skill is None:
                skill = Skill(position=skill_position, title=skill_seed.title, kind=skill_seed.kind)
                unit.skills.append(skill)
            lessons = {lesson.position: lesson for lesson in skill.lessons}
            for lesson_position, exercise_seeds in enumerate(skill_seed.lessons, start=1):
                lesson = lessons.get(lesson_position)
                if lesson is None:
                    lesson = Lesson(position=lesson_position)
                    skill.lessons.append(lesson)
                if not lesson.exercises:
                    lesson.exercises.extend(
                        _exercise(position, seed) for position, seed in enumerate(exercise_seeds, start=1)
                    )
    db.flush()


def _exercise(position: int, seed: spanish.ExerciseSeed) -> Exercise:
    match seed:
        case spanish.Choice(prompt, language, answer, wrong):
            return Exercise(
                position=position,
                type=ExerciseType.MULTIPLE_CHOICE,
                prompt=prompt,
                prompt_language=language,
                options=_choices(answer, wrong),
            )
        case spanish.Tiles(prompt, language, answers, distractors):
            return Exercise(
                position=position,
                type=ExerciseType.WORD_BANK,
                prompt=prompt,
                prompt_language=language,
                options=_tiles(spanish.tile_words(answers[0]) + distractors),
                accepted_answers=_accepted(answers),
            )
        case spanish.Pairs(pairs):
            return Exercise(
                position=position,
                type=ExerciseType.MATCH_PAIRS,
                options=[
                    ExerciseOption(position=i, text=spanish_text, match_text=english_text)
                    for i, (spanish_text, english_text) in enumerate(pairs, start=1)
                ],
            )
        case spanish.Blank(prompt, answer, wrong):
            return Exercise(
                position=position,
                type=ExerciseType.FILL_BLANK,
                prompt=prompt,
                prompt_language="es",
                options=_choices(answer, wrong),
            )
        case spanish.Typed(prompt, language, answers):
            return Exercise(
                position=position,
                type=ExerciseType.TYPE_ANSWER,
                prompt=prompt,
                prompt_language=language,
                accepted_answers=_accepted(answers),
            )
        case spanish.Listen(sentence, distractors):
            return Exercise(
                position=position,
                type=ExerciseType.LISTEN,
                prompt=sentence,
                prompt_language="es",
                options=_tiles(spanish.tile_words(sentence) + distractors),
                accepted_answers=_accepted([sentence]),
            )
        case _:
            assert_never(seed)


def _choices(answer: str, wrong: list[str]) -> list[ExerciseOption]:
    return [
        ExerciseOption(position=i, text=text, is_correct=text == answer)
        for i, text in enumerate([answer, *wrong], start=1)
    ]


def _tiles(words: list[str]) -> list[ExerciseOption]:
    return [ExerciseOption(position=i, text=word) for i, word in enumerate(words, start=1)]


def _accepted(answers: list[str]) -> list[AcceptedAnswer]:
    return [AcceptedAnswer(text=text, is_primary=i == 0) for i, text in enumerate(answers)]


def _seed_achievements(db: Session) -> None:
    existing = {achievement.key: achievement for achievement in db.scalars(select(Achievement))}
    for position, (key, title, description, metric, thresholds) in enumerate(data.ACHIEVEMENTS):
        achievement = existing.get(key)
        if achievement is None:
            achievement = Achievement(
                key=key, position=position, title=title, description=description, metric=metric
            )
            db.add(achievement)
        seeded_tiers = {tier.tier for tier in achievement.tiers}
        for tier, threshold in enumerate(thresholds, start=1):
            if tier not in seeded_tiers:
                achievement.tiers.append(AchievementTier(tier=tier, threshold=threshold))
    db.flush()


def _seed_leagues(db: Session) -> None:
    existing = set(db.scalars(select(League.name)))
    for position, (name, promotion_count, demotion_count) in enumerate(data.LEAGUES, start=1):
        if name not in existing:
            db.add(
                League(
                    position=position,
                    name=name,
                    promotion_count=promotion_count,
                    demotion_count=demotion_count,
                )
            )
    db.flush()


def _seed_rivals(db: Session, now: datetime) -> None:
    """The learners in the learner's league. Their XP is simulated from the start of this league week."""
    existing = set(db.scalars(select(User.username)))
    course = db.scalar(select(Course).where(Course.learning_language == "es", Course.from_language == "en"))
    week_began = datetime.combine(week_start_of(now.date()), time(), UTC)
    for index, (name, daily_xp, active_days) in enumerate(data.RIVALS):
        username = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
        if username in existing:
            continue
        rival = User(
            username=username,
            display_name=name,
            created_at=now - timedelta(days=30 + 11 * index),
            active_course=course,
            hearts_updated_at=now,
        )
        db.add(rival)
        db.flush()
        db.add(
            Rival(user_id=rival.id, daily_xp=daily_xp, active_days=active_days, simulated_until=week_began)
        )
    db.flush()


def _seed_default_learner(db: Session, username: str, now: datetime) -> User:
    learner = db.scalar(select(User).where(User.username == username))
    if learner is None:
        course = db.scalar(
            select(Course).where(
                Course.learning_language == data.DEFAULT_LEARNER_COURSE, Course.from_language == "en"
            )
        )
        learner = User(
            username=username,
            display_name=data.DEFAULT_LEARNER_NAME,
            created_at=now - timedelta(days=max(days for days, _ in data.DEMO_HISTORY)),
            active_course=course,
            daily_goal_xp=data.DEFAULT_LEARNER_DAILY_GOAL_XP,
            gems=STARTING_GEMS,
            hearts_updated_at=now,
        )
        db.add(learner)
        db.flush()
        _seed_demo_history(db, learner, now)
    if learner.settings is None:
        learner.settings = UserSettings()
    return learner


def _seed_demo_history(db: Session, learner: User, now: datetime) -> None:
    """Finish the first few lessons of the learner's course on past days (data.DEMO_HISTORY), writing
    the same rows a real lesson would: a session, an XP event, path progress, XP total and streak."""
    lessons = db.scalars(
        select(Lesson)
        .join(Lesson.skill)
        .join(Skill.unit)
        .where(Unit.course_id == learner.active_course_id)
        .order_by(Unit.position, Skill.position, Lesson.position)
    ).all()
    days_ago_per_lesson = [days for days, count in data.DEMO_HISTORY for _ in range(count)]

    progress: dict[int, UserSkillProgress] = {}
    for index, (lesson, days_ago) in enumerate(zip(lessons, days_ago_per_lesson, strict=False)):
        finished_at = now - timedelta(days=days_ago) + timedelta(minutes=5 * index)
        session = LessonSession(
            user_id=learner.id,
            lesson=lesson,
            mode=SessionMode.LESSON,
            status=SessionStatus.COMPLETED,
            started_at=finished_at - timedelta(minutes=3),
            finished_at=finished_at,
            xp_earned=LESSON_XP,
        )
        db.add(session)
        db.add(
            XpEvent(
                user_id=learner.id,
                session=session,
                amount=LESSON_XP,
                source=XpSource.LESSON,
                earned_at=finished_at,
                local_date=local_date(finished_at, learner.timezone),
            )
        )
        skill_progress = progress.setdefault(
            lesson.skill_id,
            UserSkillProgress(user_id=learner.id, skill_id=lesson.skill_id, lessons_completed=0),
        )
        skill_progress.lessons_completed += 1
        if skill_progress.lessons_completed == len(lesson.skill.lessons):
            skill_progress.completed_at = finished_at
        learner.total_xp += LESSON_XP

    db.add_all(progress.values())
    learner.current_streak = learner.longest_streak = len(data.DEMO_HISTORY)
    learner.last_streak_date = local_date(
        now - timedelta(days=min(days for days, _ in data.DEMO_HISTORY)), learner.timezone
    )

    # Leaderboards normally open after 10 lessons; the demo learner is already in this week's Bronze
    # league, with the rivals, so the leaderboard has something to show straight away.
    bronze = db.scalar(select(League).order_by(League.position))
    week = week_start_of(local_date(now, learner.timezone))
    for user_id in [learner.id, *db.scalars(select(Rival.user_id))]:
        if db.get(LeagueMembership, (user_id, week)) is None:
            db.add(LeagueMembership(user_id=user_id, week_start=week, league=bronze, joined_at=now))
