"""Weekly leagues: standings, rivals' XP, the end of a week, and unlocking leaderboards."""

from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import League, User, XpEvent, XpSource
from app.services.leagues import Outcome, outcome
from tests.conftest import NOW, FixedClock
from tests.test_achievements import play_lesson
from tests.test_me import get_started
from tests.test_sessions import nodes, start, start_active


def board(client: TestClient) -> dict:
    response = client.get("/api/v1/leaderboard")
    assert response.status_code == 200
    return response.json()


def me_in(standings: list[dict]) -> dict:
    return next(row for row in standings if row["is_me"])


def test_the_demo_learner_is_in_this_weeks_bronze_league(client: TestClient) -> None:
    league = board(client)

    assert (league["unlocked"], league["joined"], league["league"]["name"]) == (True, True, "Bronze")
    assert (league["week_start"], league["week_ends_at"]) == ("2026-10-05", "2026-10-12T00:00:00Z")
    assert [league["name"] for league in league["leagues"]][::9] == ["Bronze", "Diamond"]
    standings = league["standings"]
    assert [row["rank"] for row in standings] == list(range(1, 31))  # the learner and 29 rivals
    assert [row["xp"] for row in standings] == sorted((row["xp"] for row in standings), reverse=True)
    assert me_in(standings)["xp"] == 30  # the demo history's 3 lessons, all this week
    assert sum(row["xp"] for row in standings) > 30  # the rivals have been practising since Monday
    assert (league["last_result"], league["top_three_finishes"]) == (None, 0)


def test_rivals_earn_xp_as_the_week_goes_on(client: TestClient, db: Session, clock: FixedClock) -> None:
    def rival_xp() -> int:
        return sum(row["xp"] for row in board(client)["standings"] if not row["is_me"])

    def events() -> int:
        return db.scalar(select(func.count()).select_from(XpEvent))

    thursday = rival_xp()
    written = events()
    assert rival_xp() == thursday and events() == written  # reading again writes nothing new

    clock.advance(timedelta(days=1))
    assert rival_xp() > thursday


def test_a_lesson_moves_the_learner_up(client: TestClient, db: Session) -> None:
    before = me_in(board(client)["standings"])

    play_lesson(client, db, start_active(client))

    after = me_in(board(client)["standings"])
    assert after["xp"] == before["xp"] + 10
    assert after["rank"] < before["rank"]


def test_the_end_of_a_week_decides_the_next_league(
    client: TestClient, db: Session, learner: User, clock: FixedClock
) -> None:
    # A huge day this week puts the learner first.
    db.add(
        XpEvent(user_id=learner.id, amount=1000, source=XpSource.LESSON, earned_at=NOW, local_date=NOW.date())
    )
    db.commit()
    clock.advance(timedelta(days=4))  # Monday 12 October: last week is over

    league = board(client)

    result = league["last_result"]
    assert (result["week_start"], result["rank"], result["outcome"]) == ("2026-10-05", 1, "promoted")
    assert (result["league"]["name"], result["next_league"]["name"]) == ("Bronze", "Silver")
    assert (league["joined"], league["league"]["name"], league["standings"]) == (False, "Silver", [])
    assert league["top_three_finishes"] == 1

    # This week's first lesson joins the Silver League, rivals included.
    done = play_lesson(client, db, start(client, nodes(client)[0]["id"]))
    league = board(client)
    assert done["leaderboard_unlocked"] is False  # it was already unlocked
    assert (league["joined"], league["league"]["name"], len(league["standings"])) == (True, "Silver", 30)
    assert me_in(league["standings"])["xp"] == 5  # a practice session this week


@pytest.mark.parametrize(
    ("league", "rank", "expected"),
    [
        ("Silver", 7, Outcome.PROMOTED),
        ("Silver", 8, Outcome.STAYED),
        ("Silver", 25, Outcome.STAYED),
        ("Silver", 26, Outcome.DEMOTED),
        ("Bronze", 30, Outcome.STAYED),  # nowhere lower to go
        ("Diamond", 1, Outcome.STAYED),  # nowhere higher to go
    ],
)
def test_the_top_move_up_the_bottom_move_down(db: Session, league: str, rank: int, expected: Outcome) -> None:
    competing = db.scalars(select(League).where(League.name == league)).one()
    assert outcome(competing, rank, members=30) == expected


def test_leaderboards_unlock_after_ten_lessons(client: TestClient, db: Session) -> None:
    client.post("/api/v1/me/onboarding", json=get_started(client))  # a new learner, with no league
    db.scalars(select(User).where(User.username == "guest")).one().is_guest = False  # ...and a profile
    db.commit()
    league = board(client)
    assert (league["unlocked"], league["lessons_to_unlock"], league["league"]) == (False, 10, None)

    first_node = nodes(client)[0]["id"]  # its two lessons, then practice
    unlocked = [play_lesson(client, db, start(client, first_node))["leaderboard_unlocked"] for _ in range(10)]

    assert unlocked == [False] * 9 + [True]
    league = board(client)
    assert (league["unlocked"], league["lessons_to_unlock"], league["joined"]) == (True, 0, True)
    # The rivals and the demo learner are in this week's Bronze league already.
    assert (league["league"]["name"], len(league["standings"])) == ("Bronze", 31)
