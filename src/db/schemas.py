from pydantic import BaseModel, ConfigDict
import datetime


class UserMessageCreate(BaseModel):
    name: str
    text: str


class UserMessageFull(UserMessageCreate):
    id: int
    date: datetime.datetime
    model_config = ConfigDict(from_attributes=True)


class MessageStatistics(BaseModel):
    count: int
    model_config = ConfigDict(from_attributes=True)
