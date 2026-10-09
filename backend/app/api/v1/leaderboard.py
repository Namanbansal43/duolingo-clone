from fastapi import APIRouter
from sqlalchemy import select

from app.core.errors import error_response
from app.deps import ClockDep, CurrentUser, DbSession
from app.models import League
from app.schemas.leaderboard import LeaderboardOut, LeagueOut, StandingOut, WeekResultOut
from app.services.leagues import leaderboard

router = APIRouter(
    prefix="/leaderboard",
    tags=["leaderboard"],
    responses={503: error_response("`learner_missing`: the default learner has not been seeded.")},
)


@router.get("", response_model=LeaderboardOut)
def get_leaderboard(user: CurrentUser, db: DbSession, clock: ClockDep) -> LeaderboardOut:
    """This week's league: everyone's XP so far, ranked, with the zones that move up and down. Reading it
    first writes the rivals' XP up to now and ranks any league week that has ended."""
    board = leaderboard(db, user, clock.now())
    db.commit()
    leagues = db.scalars(select(League).order_by(League.position))
    return LeaderboardOut(
        unlocked=board.league is not None,
        lessons_to_unlock=board.lessons_to_unlock,
        leagues=[LeagueOut.model_validate(league) for league in leagues],
        league=LeagueOut.model_validate(board.league) if board.league else None,
        joined=board.joined,
        week_start=board.week_start,
        week_ends_at=board.week_ends_at,
        standings=[
            StandingOut(
                rank=standing.rank,
                user_id=standing.user_id,
                display_name=standing.display_name,
                xp=standing.xp,
                is_me=standing.user_id == user.id,
            )
            for standing in board.standings
        ],
        last_result=(
            WeekResultOut(
                week_start=board.last_result.week_start,
                league=LeagueOut.model_validate(board.last_result.league),
                rank=board.last_result.rank,
                outcome=board.last_result.outcome,
                next_league=LeagueOut.model_validate(board.last_result.next_league),
            )
            if board.last_result
            else None
        ),
        top_three_finishes=board.top_three_finishes,
    )
