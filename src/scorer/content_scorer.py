"""
Content Scorer - Bewertet SEO-Content nach SISTRIX-inspirierten Metriken
"""

from typing import Dict, List
import re
from bs4 import BeautifulSoup
from src.scorer.keyword_analyzer import KeywordAnalyzer
from src.scorer.readability_checker import ReadabilityChecker
from src.utils.logger import get_logger


class ContentScorer:
    """Bewertet Content-Qualität mit umfassendem Scoring-System"""
    
    def __init__(self, config):
        """
        Initialisiere Content Scorer
        
        Args:
            config: Config-Objekt
        """
        self.config = config
        self.logger = get_logger()
        self.keyword_analyzer = KeywordAnalyzer(config)
        self.readability_checker = ReadabilityChecker(config)
        
        # Gewichtungen aus Config
        self.weights = config.get("scoring.weights", {
            "keyword_optimization": 0.20,
            "structure_readability": 0.25,
            "content_quality": 0.30,
            "technical_seo": 0.15,
            "engagement": 0.10
        })
    
    def score(self, text: str, keyword: str, competitor_data: Dict) -> Dict:
        """
        Berechne umfassenden Content Score
        
        Args:
            text: Zu bewertender Text (kann HTML oder Plain Text sein)
            keyword: Haupt-Keyword
            competitor_data: Daten der Konkurrenzanalyse
            
        Returns:
            Scoring-Ergebnis mit Breakdown
        """
        self.logger.debug(f"Berechne Content Score für Keyword: '{keyword}'")
        
        # Parse HTML falls vorhanden
        soup = BeautifulSoup(text, 'html.parser')
        plain_text = soup.get_text() if text.strip().startswith('<') else text
        
        # 1. Keyword-Optimierung (20%)
        keyword_score = self._score_keyword_optimization(text, plain_text, keyword, competitor_data)
        
        # 2. Struktur & Lesbarkeit (25%)
        structure_score = self._score_structure_readability(text, plain_text, soup)
        
        # 3. Content-Qualität (30%)
        quality_score = self._score_content_quality(plain_text, competitor_data)
        
        # 4. Technisches SEO (15%)
        technical_score = self._score_technical_seo(text, soup, keyword)
        
        # 5. Engagement-Faktoren (10%)
        engagement_score = self._score_engagement(text, soup)
        
        # Berechne Gesamt-Score
        total_score = (
            keyword_score['score'] * self.weights['keyword_optimization'] +
            structure_score['score'] * self.weights['structure_readability'] +
            quality_score['score'] * self.weights['content_quality'] +
            technical_score['score'] * self.weights['technical_seo'] +
            engagement_score['score'] * self.weights['engagement']
        )
        
        result = {
            'total_score': round(total_score, 2),
            'keyword_optimization': keyword_score,
            'structure_readability': structure_score,
            'content_quality': quality_score,
            'technical_seo': technical_score,
            'engagement': engagement_score,
            'grade': self._get_grade(total_score)
        }
        
        self.logger.debug(f"✓ Content Score: {result['total_score']}/100 ({result['grade']})")
        
        return result
    
    def _score_keyword_optimization(self, text: str, plain_text: str, keyword: str, competitor_data: Dict) -> Dict:
        """Score: Keyword-Optimierung (20%)"""
        score = 0
        max_score = 100
        details = []
        
        # Analysiere Keywords
        kw_analysis = self.keyword_analyzer.analyze(plain_text, keyword)
        
        # 1. Haupt-Keyword Dichte (40 Punkte)
        target_density = competitor_data.get('benchmarks', {}).get('keyword_density', {}).get('avg', 1.5)
        actual_density = kw_analysis['main_keyword']['density']
        
        if 1.0 <= actual_density <= 3.0:
            density_score = 40
            details.append(f"✓ Keyword-Dichte optimal: {actual_density:.2f}%")
        elif 0.5 <= actual_density < 1.0 or 3.0 < actual_density <= 4.0:
            density_score = 25
            details.append(f"⚠ Keyword-Dichte akzeptabel: {actual_density:.2f}%")
        else:
            density_score = 10
            details.append(f"✗ Keyword-Dichte suboptimal: {actual_density:.2f}%")
        
        score += density_score
        
        # 2. Keyword in wichtigen Positionen (30 Punkte)
        positions_score = 0
        
        # Erster Absatz
        first_paragraph = plain_text[:200].lower()
        if keyword.lower() in first_paragraph:
            positions_score += 10
            details.append("✓ Keyword im ersten Absatz")
        
        # H1 (falls HTML)
        soup = BeautifulSoup(text, 'html.parser')
        h1_tags = soup.find_all('h1')
        if any(keyword.lower() in h1.get_text().lower() for h1 in h1_tags):
            positions_score += 10
            details.append("✓ Keyword in H1")
        
        # H2 Überschriften
        h2_tags = soup.find_all('h2')
        h2_with_kw = sum(1 for h2 in h2_tags if keyword.lower() in h2.get_text().lower())
        if h2_with_kw >= 2:
            positions_score += 10
            details.append(f"✓ Keyword in {h2_with_kw} H2-Überschriften")
        elif h2_with_kw == 1:
            positions_score += 5
        
        score += positions_score
        
        # 3. LSI/Semantische Keywords (30 Punkte)
        lsi_count = len(kw_analysis['related_keywords'])
        if lsi_count >= 10:
            lsi_score = 30
            details.append(f"✓ {lsi_count} semantische Keywords gefunden")
        elif lsi_count >= 5:
            lsi_score = 20
            details.append(f"⚠ {lsi_count} semantische Keywords (mehr empfohlen)")
        else:
            lsi_score = 10
            details.append(f"✗ Nur {lsi_count} semantische Keywords")
        
        score += lsi_score
        
        return {
            'score': score,
            'max_score': max_score,
            'percentage': round(score / max_score * 100, 2),
            'details': details,
            'metrics': kw_analysis
        }
    
    def _score_structure_readability(self, text: str, plain_text: str, soup: BeautifulSoup) -> Dict:
        """Score: Struktur & Lesbarkeit (25%)"""
        score = 0
        max_score = 100
        details = []
        
        # 1. Überschriften-Struktur (40 Punkte)
        h1_count = len(soup.find_all('h1'))
        h2_count = len(soup.find_all('h2'))
        h3_count = len(soup.find_all('h3'))
        
        # H1: Genau 1
        if h1_count == 1:
            score += 15
            details.append("✓ Eine H1-Überschrift")
        elif h1_count == 0:
            details.append("✗ Keine H1-Überschrift")
        else:
            score += 5
            details.append(f"⚠ {h1_count} H1-Überschriften (nur 1 empfohlen)")
        
        # H2: Mindestens 3
        if h2_count >= 5:
            score += 15
            details.append(f"✓ {h2_count} H2-Überschriften (gute Struktur)")
        elif h2_count >= 3:
            score += 10
            details.append(f"⚠ {h2_count} H2-Überschriften (mehr empfohlen)")
        else:
            score += 5
            details.append(f"✗ Nur {h2_count} H2-Überschriften")
        
        # H3: Mindestens 2
        if h3_count >= 3:
            score += 10
            details.append(f"✓ {h3_count} H3-Überschriften")
        elif h3_count >= 2:
            score += 7
        
        # 2. Lesbarkeit (35 Punkte)
        readability = self.readability_checker.check(plain_text)
        
        flesch_score = readability['flesch_reading_ease']
        if flesch_score >= 60:
            score += 20
            details.append(f"✓ Gute Lesbarkeit (Flesch: {flesch_score:.1f})")
        elif flesch_score >= 40:
            score += 12
            details.append(f"⚠ Akzeptable Lesbarkeit (Flesch: {flesch_score:.1f})")
        else:
            score += 5
            details.append(f"✗ Schwierige Lesbarkeit (Flesch: {flesch_score:.1f})")
        
        # Durchschnittliche Satzlänge
        avg_sentence_length = readability['avg_sentence_length']
        if avg_sentence_length <= 20:
            score += 10
            details.append(f"✓ Kurze Sätze (Ø {avg_sentence_length:.1f} Wörter)")
        elif avg_sentence_length <= 25:
            score += 7
        else:
            score += 3
            details.append(f"⚠ Lange Sätze (Ø {avg_sentence_length:.1f} Wörter)")
        
        # Absatzlänge
        paragraphs = [p.strip() for p in plain_text.split('\n\n') if p.strip()]
        if paragraphs:
            avg_para_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs)
            if avg_para_length <= 100:
                score += 5
                details.append("✓ Gut strukturierte Absätze")
        
        # 3. Listen und Aufzählungen (15 Punkte)
        ul_count = len(soup.find_all('ul'))
        ol_count = len(soup.find_all('ol'))
        list_count = ul_count + ol_count
        
        if list_count >= 2:
            score += 15
            details.append(f"✓ {list_count} Listen/Aufzählungen")
        elif list_count == 1:
            score += 10
        
        # 4. Formatierung (10 Punkte)
        bold_count = len(soup.find_all(['b', 'strong']))
        if bold_count >= 3:
            score += 10
            details.append("✓ Wichtige Begriffe hervorgehoben")
        elif bold_count >= 1:
            score += 5
        
        return {
            'score': score,
            'max_score': max_score,
            'percentage': round(score / max_score * 100, 2),
            'details': details,
            'metrics': readability
        }
    
    def _score_content_quality(self, plain_text: str, competitor_data: Dict) -> Dict:
        """Score: Content-Qualität (30%)"""
        score = 0
        max_score = 100
        details = []
        
        word_count = len(plain_text.split())
        
        # 1. Textlänge vs. Konkurrenz (40 Punkte)
        target_word_count = competitor_data.get('insights', {}).get('recommended_word_count', 1000)
        
        if word_count >= target_word_count:
            length_score = 40
            details.append(f"✓ Ausreichende Länge: {word_count} Wörter")
        elif word_count >= target_word_count * 0.8:
            length_score = 30
            details.append(f"⚠ {word_count} Wörter (Ziel: {target_word_count})")
        elif word_count >= target_word_count * 0.6:
            length_score = 20
            details.append(f"⚠ Zu kurz: {word_count} Wörter")
        else:
            length_score = 10
            details.append(f"✗ Deutlich zu kurz: {word_count} Wörter")
        
        score += length_score
        
        # 2. Informationstiefe (30 Punkte)
        # Prüfe auf verschiedene Indikatoren für Tiefe
        
        # Zahlen und Fakten
        numbers = re.findall(r'\b\d+\b', plain_text)
        if len(numbers) >= 10:
            score += 10
            details.append(f"✓ {len(numbers)} Zahlen/Fakten")
        elif len(numbers) >= 5:
            score += 6
        
        # Fachbegriffe (Wörter mit Großbuchstaben oder lange Wörter)
        words = plain_text.split()
        complex_words = [w for w in words if len(w) > 12]
        if len(complex_words) >= 20:
            score += 10
            details.append("✓ Fachliche Tiefe erkennbar")
        elif len(complex_words) >= 10:
            score += 6
        
        # Absatzanzahl (Indikator für Struktur)
        paragraphs = [p for p in plain_text.split('\n\n') if len(p.strip()) > 50]
        if len(paragraphs) >= 8:
            score += 10
            details.append(f"✓ {len(paragraphs)} Absätze (gute Gliederung)")
        elif len(paragraphs) >= 5:
            score += 6
        
        # 3. Unique Content (20 Punkte)
        # Einfache Heuristik: Verhältnis unique Wörter zu Gesamt
        unique_words = len(set(words))
        if words:
            uniqueness = unique_words / len(words)
            if uniqueness >= 0.5:
                score += 20
                details.append(f"✓ Hohe Wort-Diversität ({uniqueness:.1%})")
            elif uniqueness >= 0.4:
                score += 15
            else:
                score += 10
        
        # 4. Themenrelevanz (10 Punkte)
        # Prüfe ob häufige Konkurrenz-Themen abgedeckt sind
        common_topics = competitor_data.get('insights', {}).get('common_topics', [])
        if common_topics:
            text_lower = plain_text.lower()
            covered_topics = sum(1 for topic in common_topics[:10] if topic in text_lower)
            topic_coverage = covered_topics / min(10, len(common_topics))
            
            if topic_coverage >= 0.7:
                score += 10
                details.append(f"✓ {covered_topics}/{min(10, len(common_topics))} wichtige Themen abgedeckt")
            elif topic_coverage >= 0.5:
                score += 7
            else:
                score += 4
        
        return {
            'score': score,
            'max_score': max_score,
            'percentage': round(score / max_score * 100, 2),
            'details': details,
            'metrics': {
                'word_count': word_count,
                'paragraph_count': len(paragraphs),
                'unique_word_ratio': uniqueness if words else 0
            }
        }
    
    def _score_technical_seo(self, text: str, soup: BeautifulSoup, keyword: str) -> Dict:
        """Score: Technisches SEO (15%)"""
        score = 0
        max_score = 100
        details = []
        
        # 1. Meta-Title (30 Punkte)
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text()
            title_len = len(title)
            
            if 50 <= title_len <= 60:
                score += 20
                details.append(f"✓ Title optimal ({title_len} Zeichen)")
            elif 40 <= title_len <= 70:
                score += 15
                details.append(f"⚠ Title akzeptabel ({title_len} Zeichen)")
            else:
                score += 5
                details.append(f"✗ Title-Länge suboptimal ({title_len} Zeichen)")
            
            # Keyword im Title
            if keyword.lower() in title.lower():
                score += 10
                details.append("✓ Keyword im Title")
        else:
            details.append("✗ Kein Title-Tag")
        
        # 2. Meta-Description (30 Punkte)
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            desc = meta_desc['content']
            desc_len = len(desc)
            
            if 140 <= desc_len <= 160:
                score += 20
                details.append(f"✓ Meta-Description optimal ({desc_len} Zeichen)")
            elif 120 <= desc_len <= 180:
                score += 15
                details.append(f"⚠ Meta-Description akzeptabel ({desc_len} Zeichen)")
            else:
                score += 5
            
            # Keyword in Description
            if keyword.lower() in desc.lower():
                score += 10
                details.append("✓ Keyword in Meta-Description")
        else:
            details.append("✗ Keine Meta-Description")
        
        # 3. Bilder mit Alt-Tags (25 Punkte)
        images = soup.find_all('img')
        if images:
            images_with_alt = sum(1 for img in images if img.get('alt'))
            alt_ratio = images_with_alt / len(images)
            
            if alt_ratio >= 0.9:
                score += 25
                details.append(f"✓ {images_with_alt}/{len(images)} Bilder mit Alt-Tags")
            elif alt_ratio >= 0.7:
                score += 18
            elif alt_ratio >= 0.5:
                score += 10
            else:
                score += 5
                details.append(f"✗ Nur {images_with_alt}/{len(images)} Bilder mit Alt-Tags")
        
        # 4. HTML-Struktur (15 Punkte)
        # Semantische HTML5-Tags
        semantic_tags = soup.find_all(['article', 'section', 'header', 'footer', 'nav'])
        if len(semantic_tags) >= 2:
            score += 15
            details.append("✓ Semantisches HTML5")
        elif len(semantic_tags) >= 1:
            score += 10
        
        return {
            'score': score,
            'max_score': max_score,
            'percentage': round(score / max_score * 100, 2),
            'details': details
        }
    
    def _score_engagement(self, text: str, soup: BeautifulSoup) -> Dict:
        """Score: Engagement-Faktoren (10%)"""
        score = 0
        max_score = 100
        details = []
        
        # 1. Call-to-Actions (40 Punkte)
        cta_patterns = [
            r'\bjetzt\b', r'\bhier\b', r'\bmehr erfahren\b', r'\bkaufen\b',
            r'\bbestellen\b', r'\bkontakt\b', r'\banfrage\b', r'\bkostenlos\b'
        ]
        
        text_lower = text.lower()
        cta_count = sum(1 for pattern in cta_patterns if re.search(pattern, text_lower))
        
        if cta_count >= 3:
            score += 40
            details.append(f"✓ {cta_count} Call-to-Actions")
        elif cta_count >= 1:
            score += 25
            details.append(f"⚠ {cta_count} Call-to-Actions (mehr empfohlen)")
        
        # 2. Multimediale Elemente (30 Punkte)
        images = len(soup.find_all('img'))
        videos = len(soup.find_all(['video', 'iframe']))
        
        if images >= 3:
            score += 20
            details.append(f"✓ {images} Bilder")
        elif images >= 1:
            score += 10
        
        if videos >= 1:
            score += 10
            details.append(f"✓ {videos} Video(s)")
        
        # 3. Links (20 Punkte)
        links = soup.find_all('a', href=True)
        if len(links) >= 5:
            score += 20
            details.append(f"✓ {len(links)} Links")
        elif len(links) >= 2:
            score += 12
        
        # 4. Interaktive Elemente (10 Punkte)
        buttons = len(soup.find_all('button'))
        forms = len(soup.find_all('form'))
        
        if buttons + forms >= 1:
            score += 10
            details.append("✓ Interaktive Elemente vorhanden")
        
        return {
            'score': score,
            'max_score': max_score,
            'percentage': round(score / max_score * 100, 2),
            'details': details
        }
    
    def _get_grade(self, score: float) -> str:
        """Konvertiere Score zu Grade"""
        if score >= 90:
            return "A+ (Exzellent)"
        elif score >= 85:
            return "A (Sehr gut)"
        elif score >= 75:
            return "B (Gut)"
        elif score >= 65:
            return "C (Befriedigend)"
        elif score >= 50:
            return "D (Ausreichend)"
        else:
            return "F (Ungenügend)"
    
    def get_improvement_suggestions(self, score_result: Dict) -> List[str]:
        """
        Generiere konkrete Verbesserungsvorschläge
        
        Args:
            score_result: Scoring-Ergebnis
            
        Returns:
            Liste von Verbesserungsvorschlägen
        """
        suggestions = []
        
        # Analysiere jede Kategorie
        for category in ['keyword_optimization', 'structure_readability', 'content_quality', 'technical_seo', 'engagement']:
            cat_data = score_result.get(category, {})
            percentage = cat_data.get('percentage', 0)
            
            if percentage < 70:
                # Füge Details als Vorschläge hinzu
                for detail in cat_data.get('details', []):
                    if detail.startswith('✗') or detail.startswith('⚠'):
                        suggestions.append(detail)
        
        return suggestions
