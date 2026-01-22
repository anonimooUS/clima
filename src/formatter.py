from datetime import datetime
from src.weather import HourForecast, DaySummary


class WeatherFormatter:
    """Formatea los datos del tiempo en mensajes legibles."""

    CONDITION_ES = {
        "Clear": "Despejado",
        "Clouds": "Nublado",
        "Rain": "Lluvia",
        "Drizzle": "Llovizna",
        "Thunderstorm": "Tormenta",
        "Snow": "Nieve",
        "Mist": "Niebla",
        "Fog": "Niebla",
    }

    def format_greeting(self) -> str:
        """Saludo segun la hora."""
        hour = datetime.now().hour
        if hour < 12:
            return "☀️ Buenos dias"
        elif hour < 20:
            return "🌤️ Buenas tardes"
        else:
            return "🌙 Buenas noches"

    def format_hourly(self, forecasts: list[HourForecast]) -> str:
        """Formatea pronostico horario."""
        if not forecasts:
            return "No hay datos horarios disponibles."

        lines = ["📅 **HOY HORA A HORA**", ""]

        for f in forecasts:
            rain_indicator = f" 💧{int(f.pop * 100)}%" if f.pop > 0.2 else ""
            lines.append(
                f"  {f.time.strftime('%H:%M')}  {f.icon}  "
                f"{f.temp:.0f}°C  {f.description}{rain_indicator}"
            )

        return "\n".join(lines)

    def format_summary(self, summary: DaySummary) -> str:
        """Formatea resumen del dia."""
        condition_es = self.CONDITION_ES.get(
            summary.main_condition, summary.main_condition
        )

        rain_warning = ""
        if summary.total_pop > 0.5:
            rain_warning = (
                f"\n  ⚠️ Probabilidad de lluvia: {int(summary.total_pop * 100)}%"
            )

        return (
            f"📆 **MAÑANA** ({summary.date.strftime('%A %d')})\n\n"
            f"  🌡️ {summary.temp_min:.0f}°C - {summary.temp_max:.0f}°C\n"
            f"  🌤️ {condition_es}"
            f"{rain_warning}"
        )

    def format_full_report(
        self, hourly: list[HourForecast], tomorrow: DaySummary, city: str
    ) -> str:
        """Genera el informe completo."""
        greeting = self.format_greeting()
        date_str = datetime.now().strftime("%A, %d de %B de %Y")

        return f"""
{greeting}

🏙️ Pronostico para **{city}**
📅 {date_str}

{'─' * 35}

{self.format_hourly(hourly)}

{'─' * 35}

{self.format_summary(tomorrow)}

{'─' * 35}

_Generado automaticamente a las {datetime.now().strftime('%H:%M')}_
""".strip()
