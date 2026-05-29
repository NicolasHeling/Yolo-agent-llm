import httpx
from bs4 import BeautifulSoup
import time
import logging

logger = logging.getLogger(__name__)

class AgroScraper:
    def __init__(self):
        self.cache_data = None
        self.last_fetch_time = 0
        self.CACHE_TTL = 3600 

    async def fetch_agro_context(self):
        if self.cache_data and (time.time() - self.last_fetch_time < self.CACHE_TTL):
            return self.cache_data

        url = "https://www.noticiasagricolas.com.br/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml"
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')
                
                conteudo = soup.find('div', class_='conteudo')
                manchete = conteudo.find('h2').get_text(strip=True) if conteudo and conteudo.find('h2') else "Mercado operando com estabilidade sazonal."
                
                dados_estruturados = {
                    "status": "sucesso",
                    "fonte": "Notícias Agrícolas",
                    "manchete_do_dia": manchete,
                    "timestamp_coleta": time.strftime("%Y-%m-%d %H:%M:%S")
                }

                self.cache_data = dados_estruturados
                self.last_fetch_time = time.time()
                
                return dados_estruturados

        except httpx.TimeoutException:
            logger.warning("Timeout ao acessar fonte de notícias.")
            return {"status": "erro", "manchete_do_dia": "O portal de notícias demorou a responder."}
        except Exception as e:
            logger.error(f"Falha no Web Scraping: {str(e)}")
            return {"status": "erro", "manchete_do_dia": "Dados de mercado indisponíveis no momento."}

scraper = AgroScraper()