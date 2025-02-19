from pydantic import BaseModel, ConfigDict
import datetime


class UserBodyRequestToDB(BaseModel):
    name: str
    text: str

class UserBodyAll(UserBodyRequestToDB):
    id: int
    date: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

class MessagesCount(BaseModel):
    count: int
    model_config = ConfigDict(from_attributes=True)