import requests
import json
from datetime import datetime, timedelta

class WeatherDataService:
    """Fetches real weather data from OpenWeatherMap API"""

    def __init__(self, api_key=None):
        self.api_key = api_key or "demo"  # Use demo mode if no key provided
        self.base_url = "https://api.openweathermap.org/data/2.5"

    def get_current_weather(self, lat, lon):
        """Get current weather data for coordinates"""
        if self.api_key == "demo":
            # Return simulated data for demo mode
            return self._get_demo_weather()

        url = f"{self.base_url}/weather"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': 'metric'
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching weather: {e}")
            return self._get_demo_weather()

    def get_forecast(self, lat, lon, days=5):
        """Get 5-day weather forecast"""
        if self.api_key == "demo":
            return self._get_demo_forecast(days)

        url = f"{self.base_url}/forecast"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': 'metric'
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching forecast: {e}")
            return self._get_demo_forecast(days)

    def _get_demo_weather(self):
        """Simulated weather data for demo mode"""
        return {
            'main': {
                'temp': 32,
                'humidity': 65,
                'pressure': 1013
            },
            'wind': {
                'speed': 3.5
            },
            'weather': [{
                'description': 'partly cloudy'
            }],
            'name': 'Demo Location'
        }

    def _get_demo_forecast(self, days):
        """Simulated forecast data for demo mode"""
        forecast = []
        base_temp = 32
        for i in range(days * 8):  # 8 forecasts per day (3-hour intervals)
            temp = base_temp + (i % 5) - 2
            forecast.append({
                'dt': (datetime.now() + timedelta(hours=i*3)).timestamp(),
                'main': {
                    'temp': temp,
                    'humidity': 60 + (i % 20),
                    'pressure': 1013 + (i % 10)
                },
                'weather': [{
                    'description': 'partly cloudy' if i % 3 else 'sunny'
                }]
            })
        return {'list': forecast}

    def extract_risk_data(self, weather_data):
        """Extract relevant data for risk calculation"""
        if 'main' in weather_data:
            return {
                'temperature': weather_data['main']['temp'],
                'humidity': weather_data['main']['humidity'],
                'precipitation': 0,  # OpenWeatherMap doesn't provide this directly
                'water_usage': 150  # Default usage
            }
        return None

    def extract_forecast_data(self, forecast_data):
        """Extract time series data from forecast"""
        if 'list' in forecast_data:
            time_series = []
            for item in forecast_data['list']:
                time_series.append({
                    'timestamp': datetime.fromtimestamp(item['dt']).isoformat(),
                    'temperature': item['main']['temp'],
                    'humidity': item['main']['humidity'],
                    'description': item['weather'][0]['description']
                })
            return time_series
        return []
