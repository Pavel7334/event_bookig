from . import crud
from .database import get_db, redis_client
from .models import Event
from .tasks import send_notification
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
import json
from datetime import datetime
from prometheus_client import Counter

from .schemas import EventGet

router = APIRouter()

# Определяем метрику
events_created_total = Counter("events_created_total", "Total number of events created")

CACHE_EXPIRATION = 300  # Время жизни кэша в секундах (например, 5 минут)


@router.post("/events/", response_model=schemas.EventGet)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    new_event = crud.create_event(db=db, event=event)
    events_created_total.inc()  # Увеличиваем счётчик при создании события
    return new_event


def datetime_converter(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


@router.get("/events/", response_model=list[schemas.EventGet])
def read_events(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    # Ключ для кэша, уникальный для параметров skip и limit
    cache_key = f"events:{skip}:{limit}"

    # Проверка кэша
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)

    # Получение данных из базы данных
    events = db.query(models.Event).offset(skip).limit(limit).all()

    if not events:
        raise HTTPException(status_code=404, detail="Events not found")

    # Преобразование данных для кэширования
    events_data = [event.__dict__ for event in events]
    for event in events_data:
        event.pop("_sa_instance_state", None)  # Убираем служебные данные SQLAlchemy

    # Сериализация данных с учетом datetime
    serialized_data = json.dumps(events_data, default=datetime_converter)
    redis_client.setex(cache_key, CACHE_EXPIRATION, serialized_data)

    return json.loads(serialized_data)  # Возвращаем десериализованные данные


# Функция для конвертации datetime в строку
def datetime_converter(o):
    if isinstance(o, datetime):
        return o.isoformat()


@router.get("/events/{event_id}", response_model=schemas.EventGet)
async def read_event(event_id: int, db: Session = Depends(get_db)):
    cache_key = f"event:{event_id}"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        return json.loads(cached_data)

    # Используем SQLAlchemy модель для запроса из базы данных
    event_data = db.query(Event).filter(Event.id == event_id).first()

    if event_data is None:
        raise HTTPException(status_code=404, detail="Event not found")

    # Преобразуем SQLAlchemy модель в Pydantic
    event_data_serializable = EventGet.from_orm(event_data)

    # Сохраняем сериализованные данные в Redis
    redis_client.setex(cache_key, 3600, event_data_serializable.json())

    return event_data_serializable


@router.put("/events/{event_id}", response_model=schemas.EventGet)
def update_event(event_id: int, event: schemas.EventUpdate, db: Session = Depends(get_db)):
    db_event = crud.get_event(db, event_id=event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    updated_event = crud.update_event(db=db, event_id=event_id, event=event)

    # Удаляем кэшированное событие, чтобы при следующем запросе данные обновились
    cache_key = f"event:{event_id}"
    redis_client.delete(cache_key)

    # Сериализация обновленного события с учетом datetime
    serialized_updated_event = json.dumps(updated_event.__dict__, default=datetime_converter)
    redis_client.setex(cache_key, CACHE_EXPIRATION,
                       serialized_updated_event)  # Можно также кэшировать обновленное событие

    return json.loads(serialized_updated_event)  # Возвращаем десериализованные данные


@router.delete("/events/{event_id}", response_model=schemas.EventGet)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    db_event = crud.get_event(db, event_id=event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    deleted_event = crud.delete_event(db=db, event_id=event_id)

    # Удаляем кэшированные данные о событии
    cache_key = f"event:{event_id}"
    redis_client.delete(cache_key)

    return deleted_event


@router.post("/book_event/{event_id}")
async def book_event(event_id: int, user_email: str, db: Session = Depends(get_db)):
    event = crud.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Отправка уведомления асинхронно через Celery
    send_notification.delay(user_email, event.name)
    return {"status": "Бронирование успешно, уведомление отправлено"}