import httpx
from bs4 import BeautifulSoup
import time

class AgroScraper:
    def __init__(self):
        # Cache simples para não sobrecarregar o site alvo
        self.cache_data = None
        self.last_fetch_time = 0
        self.CACHE_TTL = 3600 # 1 hora de cache em segundos

    async def fetch_agro_context(self):
        """Busca notícias e cotações públicas para dar contexto ao LLM."""
        
        # Retorna o cache se ainda for válido
        if self.cache_data and (time.time() - self.last_fetch_time < self.CACHE_TTL):
            return self.cache_data

        url = "https://www.noticiasagricolas.com.br/" # Fonte pública
        headers = {"User-Agent": "AgroVision-Bot/1.0"}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')
                
                conteudo = soup.find('div', class_='conteudo')
                manchete = conteudo.find('h2').get_text(strip=True) if conteudo and conteudo.find('h2') else "Mercado agrícola operando com estabilidade."
                
                dados_estruturados = {
                    "status": "sucesso",
                    "fonte": "Notícias Agrícolas",
                    "manchete_do_dia": manchete,
                    "timestamp_coleta": time.strftime("%Y-%m-%d %H:%M:%S")
                }

                # Atualiza o cache
                self.cache_data = dados_estruturados
                self.last_fetch_time = time.time()
                
                return dados_estruturados

        except Exception as e:
            print(f"⚠️ Falha no Web Scraping: {str(e)}")
            return {
                "status": "erro",
                "manchete_do_dia": "Não foi possível obter dados de mercado no momento."
            }

# Instância global do scraper
scraper = AgroScraper()