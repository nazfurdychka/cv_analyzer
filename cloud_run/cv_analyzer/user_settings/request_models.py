from pydantic import BaseModel, Field


class UserSettings(BaseModel):
    chatId: str
    probabilityRangesCount: int = Field(..., gt=1, lt=6)
