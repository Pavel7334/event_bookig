from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud, schemas
from .database import get_db  # Импортируем функцию get_db

router = APIRouter()


@router.post("/events/", response_model=schemas.Event)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):  # Используем get_db
    return crud.create_event(db=db, event=event)


@router.get("/events/", response_model=list[schemas.Event])
def read_events(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):  # Используем get_db
    events = crud.get_events(db, skip=skip, limit=limit)
    return events


@router.get("/events/{event_id}", response_model=schemas.Event)
def read_event(event_id: int, db: Session = Depends(get_db)):  # Используем get_db
    db_event = crud.get_event(db, event_id=event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event
