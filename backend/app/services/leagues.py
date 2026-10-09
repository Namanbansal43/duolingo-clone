"""Weekly leagues: who competes with whom, the standings, and moving up or down when a week ends.

A league week runs Monday to Sunday in the learner's time zone. Once leaderboards are unlocked, the first
session finished in a week joins that week's league, together with the seeded rivals (they follow the
learner from league to league: they exist to compete with them). Nothing runs on a timer: whenever the
leaderboard is read or joined, the rivals' XP is written up to that moment and finished weeks are ranked.
"""

import random
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from enum import StrEnum
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import League, LeagueMembership, Rival, User, XpEvent, XpSource
from app.services.learner import lessons_completed
from app.services.rules import LEADERBOARD_UNLOCK_LESSONS
from app.services.streak import local_date


class Outcome(StrEnum):
    PROMOTED = "promoted"
    STAYED = "stayed"
    DEMOTED = "demoted"


@dataclass(frozen=True)
class Standing:
    rank: int
    user_id: int
    display_name: str
    xp: int


@dataclass(frozen=True)
class WeekResult:
    week_start: date
    league: League
    rank: int
    outcome: Outcome
    next_league: League


@dataclass(frozen=True)
class Leaderboard:
    lessons_to_unlock: int  # 0 once unlocked
    league: League | None  # this week's league: joined, or the one the next session joins; None if locked
    joined: bool
    week_start: date
    week_ends_at: datetime
    standings: list[Standing]  # empty until joined
    last_result: WeekResult | None
    top_three_finishes: int


def week_start_of(day: date) -> date:
    """The Monday of the league week `day` falls in."""
    return day - timedelta(days=day.weekday())


def week_ends_at(week_start: date, timezone: str) -> datetime:
    """A league week ends at midnight before the next Monday, in the learner's time zone."""
    return datetime.combine(week_start + timedelta(days=7), time(), ZoneInfo(timezone)).astimezone(UTC)


def outcome(league: League, rank: int, members: int) -> Outcome:
    """The top `promotion_count` move up a league and the bottom `demotion_count` move down."""
    if rank <= league.promotion_count:
        return Outcome.PROMOTED
    if rank > members - league.demotion_count:
        return Outcome.DEMOTED
    return Outcome.STAYED


def leaderboard(db: Session, user: User, now: datetime) -> Leaderboard:
    """The learner's league this week, with everyone's XP so far, after bringing leagues up to `now`."""
    refresh_leagues(db, user, now)
    start = week_start_of(local_date(now, user.timezone))
    membership = db.get(LeagueMembership, (user.id, start))
    latest = _latest_settled(db, user)
    unlocked_by = max(0, LEADERBOARD_UNLOCK_LESSONS - lessons_completed(db, user))
    return Leaderboard(
        lessons_to_unlock=0 if membership or latest else unlocked_by,
        league=_this_weeks_league(db, user, start),
        joined=membership is not None,
        week_start=start,
        week_ends_at=week_ends_at(start, user.timezone),
        standings=standings(db, start, membership.league_id) if membership else [],
        last_result=_result(db, latest) if latest else None,
        top_three_finishes=db.scalar(
            select(func.count())
            .select_from(LeagueMembership)
            .where(LeagueMembership.user_id == user.id, LeagueMembership.final_rank <= 3)
        ),
    )


def join_league(db: Session, user: User, now: datetime) -> bool:
    """Called when a session is finished: join this week's league if leaderboards are unlocked and the
    learner hasn't joined yet. Returns True when this unlocked leaderboards (the learner's first league)."""
    refresh_leagues(db, user, now)
    start = week_start_of(local_date(now, user.timezone))
    if db.get(LeagueMembership, (user.id, start)) is not None:
        return False
    league = _this_weeks_league(db, user, start)
    if league is None:
        return False
    first = db.scalar(select(LeagueMembership).where(LeagueMembership.user_id == user.id)) is None
    db.add(LeagueMembership(user_id=user.id, week_start=start, league=league, joined_at=now))
    for rival in db.scalars(select(Rival)):
        membership = db.get(LeagueMembership, (rival.user_id, start))
        if membership is None:
            db.add(LeagueMembership(user_id=rival.user_id, week_start=start, league=league, joined_at=now))
        else:
            membership.league = league
    db.flush()
    return first


def refresh_leagues(db: Session, user: User, now: datetime) -> None:
    """Bring leagues up to `now`: the rivals' XP so far, and final ranks for the learner's finished weeks."""
    simulate_rivals(db, now)
    this_week = week_start_of(local_date(now, user.timezone))
    unsettled = db.scalars(
        select(LeagueMembership)
        .where(
            LeagueMembership.user_id == user.id,
            LeagueMembership.final_rank.is_(None),
            LeagueMembership.week_start < this_week,
        )
        .order_by(LeagueMembership.week_start)
    ).all()
    for membership in unsettled:
        for standing in standings(db, membership.week_start, membership.league_id):
            db.get(LeagueMembership, (standing.user_id, membership.week_start)).final_rank = standing.rank
    db.flush()


def standings(db: Session, week_start: date, league_id: int) -> list[Standing]:
    """Everyone in one league in one week, by XP earned that week (ties: who joined first)."""
    week_xp = (
        select(XpEvent.user_id, func.sum(XpEvent.amount).label("xp"))
        .where(XpEvent.local_date.between(week_start, week_start + timedelta(days=6)))
        .group_by(XpEvent.user_id)
        .subquery()
    )
    xp = func.coalesce(week_xp.c.xp, 0)
    rows = db.execute(
        select(User.id, User.display_name, xp)
        .join(LeagueMembership, LeagueMembership.user_id == User.id)
        .outerjoin(week_xp, week_xp.c.user_id == User.id)
        .where(LeagueMembership.week_start == week_start, LeagueMembership.league_id == league_id)
        .order_by(xp.desc(), LeagueMembership.joined_at, User.id)
    ).all()
    return [
        Standing(rank=rank, user_id=user_id, display_name=name, xp=points)
        for rank, (user_id, name, points) in enumerate(rows, start=1)
    ]


def simulate_rivals(db: Session, now: datetime) -> None:
    """Write each rival's XP up to `now`. A rival's day is fixed by their id and the date, so the result
    is the same however often, or however late, this runs."""
    for rival, user in db.execute(select(Rival, User).join(User, User.id == Rival.user_id)):
        if rival.simulated_until >= now:
            continue
        day = rival.simulated_until.date()
        while day <= now.date():
            for earned_at, amount in rival_sessions(rival, day):
                if rival.simulated_until < earned_at <= now:
                    db.add(
                        XpEvent(
                            user_id=user.id,
                            amount=amount,
                            source=XpSource.LESSON,
                            earned_at=earned_at,
                            local_date=day,
                        )
                    )
                    user.total_xp += amount
            day += timedelta(days=1)
        rival.simulated_until = now


def rival_sessions(rival: Rival, day: date) -> list[tuple[datetime, int]]:
    """When a rival practises on `day` (UTC) and the XP each session earns."""
    rng = random.Random(f"rival-{rival.user_id}-{day.isoformat()}")
    if rng.random() >= rival.active_days / 7:
        return []
    count = rng.randint(1, 3)
    per_session = max(5, 5 * round(rival.daily_xp * rng.uniform(0.6, 1.4) / count / 5))
    midnight = datetime.combine(day, time(), UTC)
    times = sorted(midnight + timedelta(minutes=rng.randint(7 * 60, 23 * 60)) for _ in range(count))
    return [(at, per_session) for at in times]


def _this_weeks_league(db: Session, user: User, week_start: date) -> League | None:
    """The league the learner competes in this week: the one joined, or the one their last result leads
    to, or Bronze for a learner who has just unlocked leaderboards. None while they are locked."""
    membership = db.get(LeagueMembership, (user.id, week_start))
    if membership is not None:
        return membership.league
    latest = _latest_settled(db, user)
    if latest is not None:
        return _result(db, latest).next_league
    if lessons_completed(db, user) >= LEADERBOARD_UNLOCK_LESSONS:
        return db.scalar(select(League).order_by(League.position))
    return None


def _latest_settled(db: Session, user: User) -> LeagueMembership | None:
    return db.scalar(
        select(LeagueMembership)
        .where(LeagueMembership.user_id == user.id, LeagueMembership.final_rank.is_not(None))
        .order_by(LeagueMembership.week_start.desc())
    )


def _result(db: Session, membership: LeagueMembership) -> WeekResult:
    members = db.scalar(
        select(func.count())
        .select_from(LeagueMembership)
        .where(
            LeagueMembership.week_start == membership.week_start,
            LeagueMembership.league_id == membership.league_id,
        )
    )
    moved = outcome(membership.league, membership.final_rank, members)
    step = {Outcome.PROMOTED: 1, Outcome.STAYED: 0, Outcome.DEMOTED: -1}[moved]
    next_league = db.scalar(select(League).where(League.position == membership.league.position + step))
    return WeekResult(
        week_start=membership.week_start,
        league=membership.league,
        rank=membership.final_rank,
        outcome=moved,
        next_league=next_league or membership.league,
    )
