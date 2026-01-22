import asyncio
import logging
from datetime import datetime

from src.weather import WeatherService
from src.formatter import WeatherFormatter
from src.notifier import get_notifier
from config import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("weather.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


async def main():
    logger.info(f"Iniciando reporte del tiempo para {settings.city}")

    try:
        # 1. Obtener datos
        weather_service = WeatherService()
        hourly = await weather_service.get_today_hourly()
        tomorrow = await weather_service.get_tomorrow_summary()

        logger.info(f"Datos obtenidos: {len(hourly)} horas para hoy")

        # 2. Formatear mensaje
        formatter = WeatherFormatter()
        report = formatter.format_full_report(hourly, tomorrow, settings.city)

        # 3. Enviar notificacion
        notifier = get_notifier()
        success = await notifier.send(report)

        if success:
            logger.info("Notificacion enviada correctamente")
        else:
            logger.error("Error enviando notificacion")

    except Exception as e:
        logger.exception(f"Error en el proceso: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
