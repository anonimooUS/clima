from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    # Location (coordinates for Open-Meteo)
    city: str = "Barcelona"
    latitude: float = 41.3888
    longitude: float = 2.159
    timezone: str = "Europe/Madrid"

    # Notificacion
    notification_method: Literal["email", "telegram", "both"] = "email"

    # Email
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    email_from: str = ""
    email_password: str = ""  # App password de Gmail
    email_to: str = ""

    # Telegram (opcional)
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None

    model_config = {"env_file": ".env"}


settings = Settings()
