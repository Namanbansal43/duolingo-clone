from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

DarkModeChoice = Literal["system", "on", "off"]


class UserSettingsOut(BaseModel):
    """The learner's choices on the settings page's Preferences section."""

    model_config = ConfigDict(from_attributes=True)

    sound_effects: bool = Field(description="Play sounds for right and wrong answers and finished lessons.")
    animations: bool = Field(description="Animate celebrations and other motion in the app.")
    motivational_messages: bool = Field(description='Show encouragement in lessons, such as "5 in a row".')
    listening_exercises: bool = Field(description="Include listening exercises in lessons.")
    dark_mode: DarkModeChoice = Field(description="`system` follows the device; `on` or `off` overrides it.")


class UserSettingsUpdate(BaseModel):
    """Partial update: omitted (or null) fields are left unchanged."""

    model_config = ConfigDict(extra="forbid")

    sound_effects: bool | None = None
    animations: bool | None = None
    motivational_messages: bool | None = None
    listening_exercises: bool | None = None
    dark_mode: DarkModeChoice | None = None
