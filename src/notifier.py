import smtplib
import httpx
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from abc import ABC, abstractmethod
from config import settings


class Notifier(ABC):
    @abstractmethod
    async def send(self, message: str, subject: str | None = None) -> bool:
        pass


class EmailNotifier(Notifier):
    """Envio por email usando SMTP."""

    async def send(
        self, message: str, subject: str = "🌤️ Tu pronostico del dia"
    ) -> bool:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = settings.email_from
            msg["To"] = settings.email_to

            # Version texto plano
            text_part = MIMEText(message, "plain", "utf-8")
            msg.attach(text_part)

            # Version HTML (opcional, mas bonita)
            html_message = self._to_html(message)
            html_part = MIMEText(html_message, "html", "utf-8")
            msg.attach(html_part)

            with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
                server.starttls()
                server.login(settings.email_from, settings.email_password)
                server.send_message(msg)

            return True
        except Exception as e:
            print(f"Error enviando email: {e}")
            return False

    def _to_html(self, text: str) -> str:
        """Convierte el mensaje a HTML basico."""
        html = text.replace("\n", "<br>")
        html = html.replace("**", "<strong>").replace("**", "</strong>")
        return f"""
        <html>
        <body style="font-family: -apple-system, Arial, sans-serif; padding: 20px; max-width: 500px;">
            {html}
        </body>
        </html>
        """


class TelegramNotifier(Notifier):
    """Envio por Telegram Bot."""

    BASE_URL = "https://api.telegram.org"

    async def send(self, message: str, subject: str | None = None) -> bool:
        if not settings.telegram_bot_token or not settings.telegram_chat_id:
            print("Telegram no configurado")
            return False

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.BASE_URL}/bot{settings.telegram_bot_token}/sendMessage",
                    json={
                        "chat_id": settings.telegram_chat_id,
                        "text": message,
                        "parse_mode": "Markdown",
                    },
                )
                response.raise_for_status()
                return True
        except Exception as e:
            print(f"Error enviando Telegram: {e}")
            return False


class MultiNotifier(Notifier):
    """Envia por multiples canales."""

    def __init__(self, notifiers: list[Notifier]):
        self.notifiers = notifiers

    async def send(self, message: str, subject: str | None = None) -> bool:
        results = []
        for notifier in self.notifiers:
            result = await notifier.send(message, subject)
            results.append(result)
        return any(results)  # True si al menos uno funciono


def get_notifier() -> Notifier:
    """Factory que devuelve el notifier segun configuracion."""
    if settings.notification_method == "email":
        return EmailNotifier()
    elif settings.notification_method == "telegram":
        return TelegramNotifier()
    elif settings.notification_method == "both":
        return MultiNotifier([EmailNotifier(), TelegramNotifier()])
    else:
        raise ValueError(
            f"Metodo de notificacion desconocido: {settings.notification_method}"
        )
