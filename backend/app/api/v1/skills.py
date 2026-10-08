from fastapi import APIRouter

from app.core.errors import error_response
from app.deps import ClockDep, CurrentUser, DbSession
from app.schemas.path import ChestOut
from app.services.path import open_chest

router = APIRouter(prefix="/skills", tags=["path"])


@router.post(
    "/{skill_id}/open-chest",
    response_model=ChestOut,
    responses={
        404: error_response("`skill_not_found`: no path node has that id."),
        409: error_response(
            "`not_a_chest`, `skill_locked` (the chest hasn't been reached yet) or `chest_already_opened`."
        ),
        503: error_response("`learner_missing`: the default learner has not been seeded."),
        422: error_response("`validation_error`: the id in the URL is not a whole number."),
    },
)
def open_path_chest(skill_id: int, user: CurrentUser, db: DbSession, clock: ClockDep) -> ChestOut:
    """Open the treasure chest the learner has reached on the path; its gems are added to their balance."""
    gems_awarded = open_chest(db, user, skill_id, clock.now())
    return ChestOut(gems_awarded=gems_awarded, gems=user.gems)
