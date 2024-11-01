from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .redis_client import redis_client
from .schemas import User  # Предполагаем, что схема Pydantic также использует 'username'
from .database import get_db
from .models import User as UserModel  # Модель SQLAlchemy для пользователя
import json

router = APIRouter()

@router.get("/user/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    # Проверка наличия кэша в Redis
    cached_user = redis_client.get(f"user:{user_id}")
    if cached_user:
        user_data = json.loads(cached_user.decode("utf-8"))
        return {"user": user_data, "source": "cache"}

    # Поиск пользователя в базе данных, если кэша нет
    user_record = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")

    # Создаем объект User и добавляем в кэш
    user = User(id=user_record.id, username=user_record.username)
    redis_client.setex(f"user:{user_id}", 60, user.json())  # Кэшируем на 60 секунд

    return {"user": user.dict(), "source": "database"}
