from .celery_config import celery_app
import time


@celery_app.task
def send_notification(user_email: str, event_name: str):
    time.sleep(2)  # Эмуляция задержки отправки
    print(f"Уведомление отправлено пользователю {user_email} о событии {event_name}")
