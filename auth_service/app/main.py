from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db, engine
from app.models import User, Base  # Импортируем User и Base
from app.auth import hash_password, authenticate_user, create_access_token

app = FastAPI()

# Создание всех таблиц
Base.metadata.create_all(bind=engine)

@app.post("/register")
async def register_user(username: str, email: str, password: str, db: Session = Depends(get_db)):
    # Проверяем, существует ли пользователь с данным email
    user = db.query(User).filter(User.email == email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Хэшируем пароль
    hashed_password = hash_password(password)

    # Создаем нового пользователя
    new_user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully", "user": new_user.username}


@app.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = authenticate_user(db, email, password)
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
