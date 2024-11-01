from fastapi import FastAPI
from .auth_routes import router as auth_router
from .user_routes import router as user_router
from .database import engine
from .models import Base

app = FastAPI()

Base.metadata.create_all(bind=engine)

# Подключаем оба набора маршрутов
app.include_router(auth_router)
app.include_router(user_router)
