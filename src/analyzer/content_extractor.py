"""
Content Extractor für Webseiten-Analyse
Extrahiert Text, Struktur und SEO-Elemente von Konkurrenz-Seiten
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import re
from collections import Counter
from src.utils.logger import get_logger


class ContentExtractor:
    """Extrahiert und analysiert Content von Webseiten"""
    
    def __init__(self, config):
        """
        Initialisiere Content Extractor
        
        Args:
            config: Config-Objekt
        """
        self.config = config
        self.logger = get_logger()
        self.timeout = 10
    
    def extract(self, url: str) -> Dict:
        """
        Extrahiere alle relevanten Daten von einer URL
        
        Args:
            url: Zu analysierende URL
            
        Returns:
            Dictionary mit extrahierten Daten
        """
        self.logger.debug(f"Extrahiere Content von: {url}")
        
        try:
            # Hole HTML
            response = requests.get(
                url,
                timeout=self.timeout,
                headers={'User-Agent': self.config.get("google_search.user_agent")}
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extrahiere verschiedene Elemente
            data = {
                'url': url,
                'title': self._extract_title(soup),
                'meta_description': self._extract_meta_description(soup),
                'h1': self._extract_h1(soup),
                'headings': self._extract_headings(soup),
                'text_content': self._extract_text(soup),
                'word_count': 0,
                'images': self._extract_images(soup),
                'links': self._extract_links(soup),
                'keywords': [],
                'structure_score': 0
            }
            
            # Berechne Wortanzahl
            data['word_count'] = len(data['text_content'].split())
            
            # Extrahiere Keywords
            data['keywords'] = self._extract_keywords(data['text_content'])
            
            # Bewerte Struktur
            data['structure_score'] = self._calculate_structure_score(data)
            
            self.logger.debug(f"✓ Content extrahiert: {data['word_count']} Wörter")
            
            return data
            
        except requests.RequestException as e:
            self.logger.error(f"Fehler beim Abrufen von {url}: {e}")
            return self._empty_result(url)
        except Exception as e:
            self.logger.error(f"Fehler beim Extrahieren von {url}: {e}")
            return self._empty_result(url)
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extrahiere Title-Tag"""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else ""
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extrahiere Meta Description"""
        meta_tag = soup.find('meta', attrs={'name': 'description'})
        if meta_tag and meta_tag.get('content'):
            return meta_tag['content'].strip()
        return ""
    
    def _extract_h1(self, soup: BeautifulSoup) -> List[str]:
        """Extrahiere alle H1-Überschriften"""
        h1_tags = soup.find_all('h1')
        return [h1.get_text().strip() for h1 in h1_tags]
    
    def _extract_headings(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extrahiere alle Überschriften (H1-H6)"""
        headings = {}
        
        for level in range(1, 7):
            tag_name = f'h{level}'
            tags = soup.find_all(tag_name)
            headings[tag_name] = [tag.get_text().strip() for tag in tags]
        
        return headings
    
    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extrahiere Haupttext-Content"""
        # Entferne Script und Style Tags
        for script in soup(['script', 'style', 'nav', 'footer', 'header']):
            script.decompose()
        
        # Hole Text
        text = soup.get_text()
        
        # Bereinige
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _extract_images(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extrahiere Bild-Informationen"""
        images = []
        
        for img in soup.find_all('img'):
            img_data = {
                'src': img.get('src', ''),
                'alt': img.get('alt', ''),
                'title': img.get('title', '')
            }
            images.append(img_data)
        
        return images
    
    def _extract_links(self, soup: BeautifulSoup) -> Dict[str, int]:
        """Zähle interne und externe Links"""
        links = soup.find_all('a', href=True)
        
        internal = 0
        external = 0
        
        for link in links:
            href = link['href']
            if href.startswith('http'):
                external += 1
            else:
                internal += 1
        
        return {
            'internal': internal,
            'external': external,
            'total': len(links)
        }
    
    def _extract_keywords(self, text: str, top_n: int = 20) -> List[Dict[str, any]]:
        """
        Extrahiere häufigste Keywords aus Text
        
        Args:
            text: Zu analysierender Text
            top_n: Anzahl Top-Keywords
            
        Returns:
            Liste mit Keywords und Häufigkeit
        """
        # Bereinige Text
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Entferne Stopwörter (vereinfachte deutsche Stopwörter)
        stopwords = {
            'der', 'die', 'das', 'den', 'dem', 'des', 'ein', 'eine', 'einer', 'eines',
            'und', 'oder', 'aber', 'ist', 'sind', 'war', 'waren', 'wird', 'werden',
            'hat', 'haben', 'kann', 'können', 'muss', 'müssen', 'soll', 'sollen',
            'für', 'mit', 'auf', 'bei', 'von', 'zu', 'im', 'am', 'an', 'als', 'auch',
            'nicht', 'nur', 'noch', 'mehr', 'sehr', 'wie', 'was', 'wenn', 'dass',
            'sich', 'sie', 'er', 'es', 'wir', 'ihr', 'ich', 'du', 'man', 'diese',
            'dieser', 'dieses', 'alle', 'jede', 'jeder', 'jedes', 'nach', 'über',
            'aus', 'durch', 'um', 'bis', 'zum', 'zur'
        }
        
        # Tokenize
        words = text.split()
        
        # Filtere kurze Wörter und Stopwörter
        words = [w for w in words if len(w) > 3 and w not in stopwords]
        
        # Zähle
        word_counts = Counter(words)
        
        # Top Keywords
        top_keywords = []
        for word, count in word_counts.most_common(top_n):
            top_keywords.append({
                'keyword': word,
                'count': count,
                'density': count / len(words) if words else 0
            })
        
        return top_keywords
    
    def _calculate_structure_score(self, data: Dict) -> float:
        """
        Berechne Struktur-Score basierend auf SEO-Best-Practices
        
        Args:
            data: Extrahierte Daten
            
        Returns:
            Score von 0-100
        """
        score = 0
        max_score = 100
        
        # Title vorhanden (10 Punkte)
        if data['title']:
            score += 10
            # Optimale Länge (50-60 Zeichen)
            title_len = len(data['title'])
            if 50 <= title_len <= 60:
                score += 5
        
        # Meta Description vorhanden (10 Punkte)
        if data['meta_description']:
            score += 10
            # Optimale Länge (140-160 Zeichen)
            desc_len = len(data['meta_description'])
            if 140 <= desc_len <= 160:
                score += 5
        
        # H1 vorhanden und einzigartig (15 Punkte)
        if data['h1']:
            if len(data['h1']) == 1:
                score += 15
            elif len(data['h1']) > 1:
                score += 5  # Mehrere H1 sind suboptimal
        
        # Überschriften-Hierarchie (20 Punkte)
        h2_count = len(data['headings'].get('h2', []))
        h3_count = len(data['headings'].get('h3', []))
        
        if h2_count >= 3:
            score += 10
        if h3_count >= 2:
            score += 10
        
        # Content-Länge (15 Punkte)
        word_count = data['word_count']
        if word_count >= 1000:
            score += 15
        elif word_count >= 500:
            score += 10
        elif word_count >= 300:
            score += 5
        
        # Bilder mit Alt-Tags (10 Punkte)
        images = data['images']
        if images:
            images_with_alt = sum(1 for img in images if img['alt'])
            alt_ratio = images_with_alt / len(images) if images else 0
            score += int(10 * alt_ratio)
        
        # Links vorhanden (10 Punkte)
        if data['links']['total'] > 0:
            score += 10
        
        return min(score, max_score)
    
    def _empty_result(self, url: str) -> Dict:
        """Erstelle leeres Ergebnis bei Fehler"""
        return {
            'url': url,
            'title': '',
            'meta_description': '',
            'h1': [],
            'headings': {},
            'text_content': '',
            'word_count': 0,
            'images': [],
            'links': {'internal': 0, 'external': 0, 'total': 0},
            'keywords': [],
            'structure_score': 0,
            'error': True
        }
