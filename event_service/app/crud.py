from sqlalchemy.orm import Session
from . import models, schemas


# Создание события
def create_event(db: Session, event: schemas.EventCreate):
    db_event = models.Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


# Получение всех событий с пагинацией
def get_events(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Event).offset(skip).limit(limit).all()


# Получение события по ID
def get_event(db: Session, event_id: int):
    return db.query(models.Event).filter(models.Event.id == event_id).first()


# Обновление события
def update_event(db: Session, event_id: int, event: schemas.EventUpdate):
    db_event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if db_event:
        for key, value in event.dict().items():
            setattr(db_event, key, value)
        db.commit()
        db.refresh(db_event)
        return db_event
    return None


# Удаление события
def delete_event(db: Session, event_id: int):
    db_event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if db_event:
        db.delete(db_event)
        db.commit()
        return db_event
    return None
