import requests
from datetime import datetime

WEATHER_API_KEY: str = 'afa7776d81d34ecfbd4204904241707'
WEATHER_API_URL: str = 'http://api.weatherapi.com/v1/forecast.json'


def fetch_weather(location: str, date: datetime) -> dict:
    response = requests.get(WEATHER_API_URL, params={
        'key': WEATHER_API_KEY,
        'q': location,
        'dt': date.strftime('%Y-%m-%d')
    })
    response.raise_for_status()
    return response.json()