from fastapi import FastAPI
from . import models
from .database import engine
from .routers import router

from prometheus_fastapi_instrumentator import Instrumentator


# Создаем таблицы
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app, endpoint="/metrics")


app.include_router(router)
