"""
Google Search Scraper für Top 5 Ranking-Analyse
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
from urllib.parse import quote_plus
from src.utils.logger import get_logger


class GoogleScraper:
    """Scraper für Google Search Results"""
    
    def __init__(self, config):
        """
        Initialisiere Google Scraper
        
        Args:
            config: Config-Objekt
        """
        self.config = config
        self.logger = get_logger()
        self.base_url = config.get("google_search.base_url", "https://www.google.de/search")
        self.user_agent = config.get(
            "google_search.user_agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        self.results_count = config.get("google_search.results_count", 5)
    
    def search(self, keyword: str) -> List[Dict[str, str]]:
        """
        Suche nach Keyword und hole Top-Ergebnisse
        
        Args:
            keyword: Suchbegriff
            
        Returns:
            Liste mit Top-Suchergebnissen (URL, Titel, Snippet)
        """
        self.logger.info(f"Suche Google.de nach: '{keyword}'")
        
        try:
            # Search Query
            params = {
                'q': keyword,
                'hl': 'de',
                'gl': 'de',
                'num': self.results_count + 5  # Extra für Filterung
            }
            
            headers = {
                'User-Agent': self.user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                headers=headers,
                timeout=10
            )
            
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            results = self._parse_results(soup)
            
            # Filtere und limitiere
            filtered_results = self._filter_results(results)[:self.results_count]
            
            self.logger.info(f"✓ {len(filtered_results)} Suchergebnisse gefunden")
            
            return filtered_results
            
        except requests.RequestException as e:
            self.logger.error(f"Fehler bei Google-Suche: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unerwarteter Fehler: {e}")
            return []
    
    def _parse_results(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """
        Parse Suchergebnisse aus HTML
        
        Args:
            soup: BeautifulSoup-Objekt
            
        Returns:
            Liste mit geparsten Ergebnissen
        """
        results = []
        
        # Finde organische Suchergebnisse
        # Google verwendet verschiedene Selektoren, daher mehrere Varianten
        search_divs = soup.find_all('div', class_='g')
        
        for div in search_divs:
            try:
                # URL
                link_tag = div.find('a', href=True)
                if not link_tag:
                    continue
                
                url = link_tag['href']
                
                # Überspringe Google-interne Links
                if url.startswith('/search') or 'google.' in url:
                    continue
                
                # Titel
                title_tag = div.find('h3')
                title = title_tag.get_text() if title_tag else "Kein Titel"
                
                # Snippet/Description
                snippet_div = div.find('div', class_=['VwiC3b', 'yXK7lf'])
                snippet = snippet_div.get_text() if snippet_div else ""
                
                results.append({
                    'url': url,
                    'title': title,
                    'snippet': snippet,
                    'position': len(results) + 1
                })
                
            except Exception as e:
                self.logger.debug(f"Fehler beim Parsen eines Ergebnisses: {e}")
                continue
        
        return results
    
    def _filter_results(self, results: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Filtere unerwünschte Ergebnisse
        
        Args:
            results: Rohe Suchergebnisse
            
        Returns:
            Gefilterte Ergebnisse
        """
        filtered = []
        
        excluded_domains = [
            'google.com', 'google.de',
            'youtube.com', 'facebook.com',
            'wikipedia.org'  # Optional: Wikipedia ausschließen
        ]
        
        for result in results:
            url = result['url'].lower()
            
            # Überspringe ausgeschlossene Domains
            if any(domain in url for domain in excluded_domains):
                continue
            
            # Überspringe PDFs und andere Dateien
            if url.endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx')):
                continue
            
            filtered.append(result)
        
        return filtered
    
    def get_top_competitors(self, keyword: str, count: int = 5) -> List[Dict[str, str]]:
        """
        Hole Top N Konkurrenten für Keyword
        
        Args:
            keyword: Suchbegriff
            count: Anzahl der gewünschten Ergebnisse
            
        Returns:
            Top N Konkurrenten
        """
        results = self.search(keyword)
        return results[:count]
