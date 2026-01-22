import httpx
from datetime import datetime, timedelta
from dataclasses import dataclass
from config import settings


@dataclass
class HourForecast:
    time: datetime
    temp: float
    feels_like: float
    description: str
    icon: str
    pop: float  # Probability of precipitation (0-1)
    humidity: int
    wind_speed: float


@dataclass
class DaySummary:
    date: datetime
    temp_min: float
    temp_max: float
    main_condition: str
    total_pop: float  # Max probability of rain


class WeatherService:
    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    # WMO Weather interpretation codes to emoji and description
    WMO_CODES = {
        0: ("☀️", "Despejado"),
        1: ("🌤️", "Mayormente despejado"),
        2: ("⛅", "Parcialmente nublado"),
        3: ("☁️", "Nublado"),
        45: ("🌫️", "Niebla"),
        48: ("🌫️", "Niebla con escarcha"),
        51: ("🌧️", "Llovizna ligera"),
        53: ("🌧️", "Llovizna moderada"),
        55: ("🌧️", "Llovizna intensa"),
        56: ("🌧️", "Llovizna helada ligera"),
        57: ("🌧️", "Llovizna helada intensa"),
        61: ("🌦️", "Lluvia ligera"),
        63: ("🌧️", "Lluvia moderada"),
        65: ("🌧️", "Lluvia intensa"),
        66: ("🌧️", "Lluvia helada ligera"),
        67: ("🌧️", "Lluvia helada intensa"),
        71: ("❄️", "Nieve ligera"),
        73: ("❄️", "Nieve moderada"),
        75: ("❄️", "Nieve intensa"),
        77: ("❄️", "Granizo"),
        80: ("🌦️", "Chubascos ligeros"),
        81: ("🌧️", "Chubascos moderados"),
        82: ("🌧️", "Chubascos intensos"),
        85: ("🌨️", "Chubascos de nieve ligeros"),
        86: ("🌨️", "Chubascos de nieve intensos"),
        95: ("⛈️", "Tormenta"),
        96: ("⛈️", "Tormenta con granizo ligero"),
        99: ("⛈️", "Tormenta con granizo intenso"),
    }

    # Map WMO codes to general conditions for summary
    WMO_CONDITIONS = {
        0: "Clear",
        1: "Clear",
        2: "Clouds",
        3: "Clouds",
        45: "Fog",
        48: "Fog",
        51: "Drizzle",
        53: "Drizzle",
        55: "Drizzle",
        56: "Drizzle",
        57: "Drizzle",
        61: "Rain",
        63: "Rain",
        65: "Rain",
        66: "Rain",
        67: "Rain",
        71: "Snow",
        73: "Snow",
        75: "Snow",
        77: "Snow",
        80: "Rain",
        81: "Rain",
        82: "Rain",
        85: "Snow",
        86: "Snow",
        95: "Thunderstorm",
        96: "Thunderstorm",
        99: "Thunderstorm",
    }

    def __init__(self):
        self.latitude = settings.latitude
        self.longitude = settings.longitude
        self.timezone = settings.timezone

    def _code_to_emoji(self, code: int) -> str:
        """Convierte WMO code a emoji."""
        return self.WMO_CODES.get(code, ("🌡️", "Desconocido"))[0]

    def _code_to_description(self, code: int) -> str:
        """Convierte WMO code a descripcion."""
        return self.WMO_CODES.get(code, ("🌡️", "Desconocido"))[1]

    def _code_to_condition(self, code: int) -> str:
        """Convierte WMO code a condicion general."""
        return self.WMO_CONDITIONS.get(code, "Unknown")

    async def get_forecast(self) -> dict:
        """Obtiene pronostico de Open-Meteo."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.BASE_URL,
                params={
                    "latitude": self.latitude,
                    "longitude": self.longitude,
                    "hourly": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation_probability,weather_code,wind_speed_10m",
                    "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                    "timezone": self.timezone,
                    "forecast_days": 3,
                },
            )
            response.raise_for_status()
            return response.json()

    async def get_today_hourly(self) -> list[HourForecast]:
        """Pronostico hora a hora para hoy."""
        data = await self.get_forecast()
        today = datetime.now().date()

        hourly_data = data["hourly"]
        times = hourly_data["time"]

        hourly = []
        for i, time_str in enumerate(times):
            dt = datetime.fromisoformat(time_str)
            if dt.date() == today and dt.hour >= datetime.now().hour:
                weather_code = hourly_data["weather_code"][i]
                hourly.append(
                    HourForecast(
                        time=dt,
                        temp=hourly_data["temperature_2m"][i],
                        feels_like=hourly_data["apparent_temperature"][i],
                        description=self._code_to_description(weather_code),
                        icon=self._code_to_emoji(weather_code),
                        pop=hourly_data["precipitation_probability"][i] / 100,
                        humidity=hourly_data["relative_humidity_2m"][i],
                        wind_speed=hourly_data["wind_speed_10m"][i],
                    )
                )

        return hourly

    async def get_tomorrow_summary(self) -> DaySummary:
        """Resumen de manana."""
        data = await self.get_forecast()
        tomorrow = (datetime.now() + timedelta(days=1)).date()

        daily_data = data["daily"]
        times = daily_data["time"]

        for i, date_str in enumerate(times):
            dt = datetime.fromisoformat(date_str).date()
            if dt == tomorrow:
                weather_code = daily_data["weather_code"][i]
                return DaySummary(
                    date=tomorrow,
                    temp_min=daily_data["temperature_2m_min"][i],
                    temp_max=daily_data["temperature_2m_max"][i],
                    main_condition=self._code_to_condition(weather_code),
                    total_pop=daily_data["precipitation_probability_max"][i] / 100,
                )

        raise ValueError("No hay datos para manana")
