from pydantic import BaseModel, ConfigDict, Field


class CourseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    learning_language: str = Field(description="Code of the language being learned; also its flag.")
    from_language: str = Field(description="Code of the language the course is taught in.")
    title: str
    is_available: bool = Field(description="False means the course is shown as coming soon.")


class CatalogCourseOut(CourseOut):
    """A course as listed in the catalogue, with how many learners are studying it."""

    learners: int = Field(description="Learners whose active course this is.")
