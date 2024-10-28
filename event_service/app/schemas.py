from pydantic import BaseModel
from datetime import datetime


class EventBase(BaseModel):
    title: str
    description: str
    date: datetime
    location: str


class EventCreate(EventBase):
    pass


class EventUpdate(EventBase):
    pass


class Event(EventBase):
    id: int

    class Config:
        orm_mode = True
