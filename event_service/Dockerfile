# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Скопируйте файлы pyproject.toml и poetry.lock в контейнер
COPY ./pyproject.toml ./poetry.lock ./

# Обновите pip
RUN pip install --upgrade pip

# Установите Poetry
RUN pip install --no-cache-dir poetry==1.6.1

# Установите зависимости
RUN poetry config virtualenvs.create false && poetry install --no-cache --no-root

# Скопируйте остальные файлы приложения в контейнер
COPY ./app /app/app

# Устанавливаем команду запуска
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002", "--reload"]
