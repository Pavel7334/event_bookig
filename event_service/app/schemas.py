from pydantic import BaseModel
from datetime import datetime


class EventBase(BaseModel):
    title: str
    description: str
    date: datetime
    location: str

    class Config:
        orm_mode = True  # Позволяет Pydantic моделям работать с ORM объектами SQLAlchemy


class EventCreate(EventBase):
    pass


class EventUpdate(EventBase):
    pass


class EventGet(EventBase):
    id: int  # Поле id должно присутствовать в Pydantic модели для response_model

    class Config:
        orm_mode = True
