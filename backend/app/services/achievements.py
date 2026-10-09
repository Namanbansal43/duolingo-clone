"""Achievements: levels reached by passing a statistic's thresholds, e.g. Wildfire at a 3, 7, 14... day
streak.

Every statistic an achievement measures only grows (longest streak, total XP, lessons and lessons without a
mistake), so a level, once reached, is never lost. Levels are stored when a session is finished, with the
time they were reached, and the lesson's result screen announces the new ones.
"""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Achievement, AchievementMetric, User, UserAchievement
from app.services.learner import lessons_completed


@dataclass(frozen=True)
class AchievementProgress:
    achievement: Achievement
    level: int  # highest level reached; 0 before the first
    value: int  # the learner's statistic
    unlocked_at: datetime | None  # when the current level was reached

    @property
    def max_level(self) -> int:
        return len(self.achievement.tiers)

    @property
    def goal(self) -> int:
        """The next level's threshold, or the last level's once all are reached."""
        return self.achievement.tiers[min(self.level, self.max_level - 1)].threshold

    @property
    def description(self) -> str:
        return self.achievement.description.format(threshold=self.goal)


def statistics(db: Session, user: User) -> dict[str, int]:
    """The learner's value for each metric achievements measure."""
    return {
        AchievementMetric.STREAK: user.longest_streak,
        AchievementMetric.TOTAL_XP: user.total_xp,
        AchievementMetric.LESSONS_COMPLETED: lessons_completed(db, user),
        AchievementMetric.PERFECT_LESSONS: lessons_completed(db, user, perfect=True),
    }


def achievement_progress(db: Session, user: User) -> list[AchievementProgress]:
    """Every achievement, in display order, with the learner's level and progress towards the next."""
    values = statistics(db, user)
    reached = {
        (row.achievement_id, row.tier): row.unlocked_at
        for row in db.scalars(select(UserAchievement).where(UserAchievement.user_id == user.id))
    }
    progress = []
    for achievement in db.scalars(select(Achievement).order_by(Achievement.position)):
        level = max((t.tier for t in achievement.tiers if (achievement.id, t.tier) in reached), default=0)
        progress.append(
            AchievementProgress(
                achievement=achievement,
                level=level,
                value=values[achievement.metric],
                unlocked_at=reached.get((achievement.id, level)),
            )
        )
    return progress


def unlock_achievements(db: Session, user: User, now: datetime) -> list[AchievementProgress]:
    """Store every level the learner has newly reached, and return the achievements that went up (at
    their new level). The caller commits."""
    values = statistics(db, user)
    reached = {
        (achievement_id, tier)
        for achievement_id, tier in db.execute(
            select(UserAchievement.achievement_id, UserAchievement.tier).where(
                UserAchievement.user_id == user.id
            )
        )
    }
    raised = set()
    for achievement in db.scalars(select(Achievement)):
        for tier in achievement.tiers:
            if tier.threshold <= values[achievement.metric] and (achievement.id, tier.tier) not in reached:
                db.add(
                    UserAchievement(
                        user_id=user.id, achievement_id=achievement.id, tier=tier.tier, unlocked_at=now
                    )
                )
                raised.add(achievement.id)
    db.flush()
    return [p for p in achievement_progress(db, user) if p.achievement.id in raised]
