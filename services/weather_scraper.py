import httpx
import time
import logging

logger = logging.getLogger(__name__)

class WeatherScraper:
    def __init__(self):
        # API pública e gratuita
        self.api_url = "https://api.open-meteo.com/v1/forecast"
        self.cache = {}
        self.cache_ttl = 600  # Cache de 10 minutos para não estourar requisições

    async def get_current_weather(self, lat: float = -23.55, lon: float = -46.63):
        cache_key = f"{lat},{lon}"
        current_time = time.time()

        # Retorna do cache se ainda for válido
        if cache_key in self.cache and (current_time - self.cache[cache_key]['timestamp'] < self.cache_ttl):
            return self.cache[cache_key]['data']

        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": True
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.api_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                weather_code = data["current_weather"]["weathercode"]
                # Verifica códigos de chuva segundo a WMO
                is_raining = weather_code in [51, 53, 55, 61, 63, 65, 80, 81, 82]
                
                weather_info = {
                    "temperature": data["current_weather"]["temperature"],
                    "windspeed": data["current_weather"]["windspeed"],
                    "is_raining": is_raining,
                    "status": "success"
                }

                self.cache[cache_key] = {'data': weather_info, 'timestamp': current_time}
                return weather_info

        except Exception as e:
            logger.error(f"Erro no Scraper de Clima: {e}")
            return {"status": "error", "message": "Dados meteorológicos indisponíveis."}

weather_service = WeatherScraper()