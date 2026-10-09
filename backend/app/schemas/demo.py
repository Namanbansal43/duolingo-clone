from datetime import datetime

from pydantic import BaseModel, Field


class DemoClockOut(BaseModel):
    days_ahead: int = Field(description="Days the app's clock runs ahead of real time (0: no time travel).")
    now: datetime = Field(description="The app's current time, which every other endpoint goes by.")
