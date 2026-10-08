from pydantic import BaseModel, ConfigDict


class CourseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    learning_language: str
    from_language: str
    title: str
    is_available: bool
