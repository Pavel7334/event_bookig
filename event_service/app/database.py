from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import redis

DATABASE_URL = "postgresql://postgres:123@db_event:5432/event_db"

# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost:5432/event_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Подключение к Redis
redis_client = redis.StrictRedis(host="redis", port=6379, db=0, decode_responses=True)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
