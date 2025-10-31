"""
Competitor Analyzer - Analysiert Top 5 Google-Rankings
"""

from typing import Dict, List
import statistics
from src.analyzer.google_scraper import GoogleScraper
from src.analyzer.content_extractor import ContentExtractor
from src.utils.logger import get_logger


class CompetitorAnalyzer:
    """Analysiert Konkurrenz-Websites für SEO-Optimierung"""
    
    def __init__(self, config):
        """
        Initialisiere Competitor Analyzer
        
        Args:
            config: Config-Objekt
        """
        self.config = config
        self.logger = get_logger()
        self.google_scraper = GoogleScraper(config)
        self.content_extractor = ContentExtractor(config)
    
    def analyze(self, keyword: str) -> Dict:
        """
        Führe vollständige Konkurrenzanalyse durch
        
        Args:
            keyword: Zu analysierendes Keyword
            
        Returns:
            Analyse-Ergebnisse mit Benchmarks und Insights
        """
        self.logger.info(f"Starte Konkurrenzanalyse für: '{keyword}'")
        
        # 1. Hole Top 5 Google-Ergebnisse
        search_results = self.google_scraper.get_top_competitors(keyword, count=5)
        
        if not search_results:
            self.logger.warning("Keine Suchergebnisse gefunden")
            return self._empty_analysis(keyword)
        
        # 2. Extrahiere Content von jeder URL
        competitors = []
        for result in search_results:
            content_data = self.content_extractor.extract(result['url'])
            
            # Kombiniere Search-Result mit Content-Daten
            competitor = {
                **result,
                **content_data
            }
            
            competitors.append(competitor)
        
        # 3. Berechne Benchmarks
        benchmarks = self._calculate_benchmarks(competitors, keyword)
        
        # 4. Identifiziere Content-Gaps und Opportunities
        insights = self._generate_insights(competitors, keyword, benchmarks)
        
        analysis_result = {
            'keyword': keyword,
            'competitors': competitors,
            'benchmarks': benchmarks,
            'insights': insights,
            'competitor_count': len(competitors)
        }
        
        self.logger.info(f"✓ Konkurrenzanalyse abgeschlossen: {len(competitors)} Seiten analysiert")
        
        return analysis_result
    
    def _calculate_benchmarks(self, competitors: List[Dict], keyword: str) -> Dict:
        """
        Berechne Benchmark-Werte aus Konkurrenz-Daten
        
        Args:
            competitors: Liste der Konkurrenten
            keyword: Analysiertes Keyword
            
        Returns:
            Benchmark-Metriken
        """
        if not competitors:
            return {}
        
        # Sammle Metriken
        word_counts = [c['word_count'] for c in competitors if c.get('word_count', 0) > 0]
        structure_scores = [c['structure_score'] for c in competitors if 'structure_score' in c]
        
        h1_counts = [len(c.get('h1', [])) for c in competitors]
        h2_counts = [len(c.get('headings', {}).get('h2', [])) for c in competitors]
        h3_counts = [len(c.get('headings', {}).get('h3', [])) for c in competitors]
        
        image_counts = [len(c.get('images', [])) for c in competitors]
        images_with_alt = [
            sum(1 for img in c.get('images', []) if img.get('alt'))
            for c in competitors
        ]
        
        # Keyword-Dichten
        keyword_densities = []
        for c in competitors:
            text = c.get('text_content', '').lower()
            kw_lower = keyword.lower()
            if text and kw_lower:
                count = text.count(kw_lower)
                words = len(text.split())
                density = (count / words * 100) if words > 0 else 0
                keyword_densities.append(density)
        
        # Berechne Statistiken
        benchmarks = {
            'word_count': {
                'min': min(word_counts) if word_counts else 0,
                'max': max(word_counts) if word_counts else 0,
                'avg': statistics.mean(word_counts) if word_counts else 0,
                'median': statistics.median(word_counts) if word_counts else 0
            },
            'structure_score': {
                'avg': statistics.mean(structure_scores) if structure_scores else 0,
                'max': max(structure_scores) if structure_scores else 0
            },
            'headings': {
                'h1_avg': statistics.mean(h1_counts) if h1_counts else 0,
                'h2_avg': statistics.mean(h2_counts) if h2_counts else 0,
                'h3_avg': statistics.mean(h3_counts) if h3_counts else 0
            },
            'images': {
                'count_avg': statistics.mean(image_counts) if image_counts else 0,
                'with_alt_avg': statistics.mean(images_with_alt) if images_with_alt else 0
            },
            'keyword_density': {
                'avg': statistics.mean(keyword_densities) if keyword_densities else 0,
                'min': min(keyword_densities) if keyword_densities else 0,
                'max': max(keyword_densities) if keyword_densities else 0
            }
        }
        
        return benchmarks
    
    def _generate_insights(self, competitors: List[Dict], keyword: str, benchmarks: Dict) -> Dict:
        """
        Generiere Insights und Empfehlungen
        
        Args:
            competitors: Konkurrenten-Daten
            keyword: Keyword
            benchmarks: Berechnete Benchmarks
            
        Returns:
            Insights und Empfehlungen
        """
        insights = {
            'recommended_word_count': int(benchmarks['word_count']['avg'] * 1.1),  # 10% mehr
            'recommended_h2_count': max(3, int(benchmarks['headings']['h2_avg'])),
            'recommended_h3_count': max(2, int(benchmarks['headings']['h3_avg'])),
            'recommended_image_count': max(2, int(benchmarks['images']['count_avg'])),
            'target_keyword_density': benchmarks['keyword_density']['avg'],
            'common_topics': self._extract_common_topics(competitors),
            'content_gaps': self._identify_content_gaps(competitors, keyword),
            'best_practices': self._identify_best_practices(competitors)
        }
        
        return insights
    
    def _extract_common_topics(self, competitors: List[Dict]) -> List[str]:
        """
        Extrahiere häufige Themen aus Konkurrenz-Content
        
        Args:
            competitors: Konkurrenten-Daten
            
        Returns:
            Liste häufiger Themen/Keywords
        """
        # Sammle alle Keywords von allen Konkurrenten
        all_keywords = {}
        
        for competitor in competitors:
            for kw_data in competitor.get('keywords', []):
                keyword = kw_data['keyword']
                count = kw_data['count']
                
                if keyword in all_keywords:
                    all_keywords[keyword] += count
                else:
                    all_keywords[keyword] = count
        
        # Sortiere nach Häufigkeit
        sorted_keywords = sorted(
            all_keywords.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Top 15 Themen
        return [kw for kw, _ in sorted_keywords[:15]]
    
    def _identify_content_gaps(self, competitors: List[Dict], keyword: str) -> List[str]:
        """
        Identifiziere Content-Lücken und Opportunities
        
        Args:
            competitors: Konkurrenten-Daten
            keyword: Keyword
            
        Returns:
            Liste von Content-Gaps
        """
        gaps = []
        
        # Prüfe auf fehlende Elemente bei Konkurrenten
        missing_h1 = sum(1 for c in competitors if not c.get('h1'))
        if missing_h1 > 2:
            gaps.append("Viele Konkurrenten haben keine klare H1-Struktur")
        
        missing_meta_desc = sum(1 for c in competitors if not c.get('meta_description'))
        if missing_meta_desc > 2:
            gaps.append("Mehrere Konkurrenten haben keine Meta-Description")
        
        low_image_count = sum(1 for c in competitors if len(c.get('images', [])) < 2)
        if low_image_count > 3:
            gaps.append("Wenige Bilder bei Konkurrenten - Opportunity für visuellen Content")
        
        # Prüfe auf kurze Texte
        short_content = sum(1 for c in competitors if c.get('word_count', 0) < 500)
        if short_content > 2:
            gaps.append("Viele Konkurrenten haben kurze Texte - Chance für ausführlichen Content")
        
        return gaps
    
    def _identify_best_practices(self, competitors: List[Dict]) -> List[str]:
        """
        Identifiziere Best Practices von Top-Performern
        
        Args:
            competitors: Konkurrenten-Daten
            
        Returns:
            Liste von Best Practices
        """
        practices = []
        
        # Analysiere Top 3 Performer
        top_performers = sorted(
            competitors,
            key=lambda x: x.get('structure_score', 0),
            reverse=True
        )[:3]
        
        for performer in top_performers:
            # Lange, ausführliche Texte
            if performer.get('word_count', 0) > 1000:
                practices.append(f"Ausführlicher Content ({performer['word_count']} Wörter)")
            
            # Gute Überschriften-Struktur
            h2_count = len(performer.get('headings', {}).get('h2', []))
            if h2_count >= 5:
                practices.append(f"Klare Struktur mit {h2_count} H2-Überschriften")
            
            # Viele Bilder mit Alt-Tags
            images = performer.get('images', [])
            if len(images) >= 3:
                alt_count = sum(1 for img in images if img.get('alt'))
                if alt_count >= len(images) * 0.8:
                    practices.append(f"{len(images)} Bilder mit SEO-optimierten Alt-Tags")
        
        # Dedupliziere
        return list(set(practices))
    
    def _empty_analysis(self, keyword: str) -> Dict:
        """Erstelle leere Analyse bei Fehler"""
        return {
            'keyword': keyword,
            'competitors': [],
            'benchmarks': {},
            'insights': {},
            'competitor_count': 0,
            'error': True
        }
