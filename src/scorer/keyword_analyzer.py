"""
Keyword Analyzer - Analysiert Keyword-Verwendung und semantische Relevanz
"""

import re
from typing import Dict, List
from collections import Counter


class KeywordAnalyzer:
    """Analysiert Keywords und semantische Begriffe im Text"""
    
    def __init__(self, config):
        """
        Initialisiere Keyword Analyzer
        
        Args:
            config: Config-Objekt
        """
        self.config = config
    
    def analyze(self, text: str, main_keyword: str) -> Dict:
        """
        Analysiere Keyword-Verwendung im Text
        
        Args:
            text: Zu analysierender Text
            main_keyword: Haupt-Keyword
            
        Returns:
            Analyse-Ergebnisse
        """
        text_lower = text.lower()
        words = self._tokenize(text)
        
        # Haupt-Keyword Analyse
        main_kw_data = self._analyze_main_keyword(text_lower, words, main_keyword)
        
        # Verwandte Keywords
        related_kw = self._find_related_keywords(words, main_keyword)
        
        # Keyword-Positionen
        positions = self._find_keyword_positions(text, main_keyword)
        
        return {
            'main_keyword': main_kw_data,
            'related_keywords': related_kw,
            'positions': positions,
            'total_keywords': len(related_kw) + 1
        }
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenisiere Text in Wörter
        
        Args:
            text: Text
            
        Returns:
            Liste von Wörtern
        """
        # Bereinige und tokenisiere
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        
        # Filtere kurze Wörter
        words = [w for w in words if len(w) > 2]
        
        return words
    
    def _analyze_main_keyword(self, text_lower: str, words: List[str], keyword: str) -> Dict:
        """
        Analysiere Haupt-Keyword
        
        Args:
            text_lower: Text in Kleinbuchstaben
            words: Tokenisierte Wörter
            keyword: Haupt-Keyword
            
        Returns:
            Keyword-Daten
        """
        keyword_lower = keyword.lower()
        
        # Zähle Vorkommen
        count = text_lower.count(keyword_lower)
        
        # Berechne Dichte
        total_words = len(words)
        density = (count / total_words * 100) if total_words > 0 else 0
        
        # Variationen finden (Singular/Plural, etc.)
        variations = self._find_keyword_variations(words, keyword_lower)
        
        return {
            'keyword': keyword,
            'count': count,
            'density': round(density, 2),
            'variations': variations,
            'variation_count': len(variations)
        }
    
    def _find_keyword_variations(self, words: List[str], keyword: str) -> List[str]:
        """
        Finde Variationen des Keywords
        
        Args:
            words: Wortliste
            keyword: Keyword
            
        Returns:
            Liste von Variationen
        """
        variations = set()
        keyword_parts = keyword.split()
        
        # Wenn Keyword aus mehreren Wörtern besteht
        if len(keyword_parts) > 1:
            # Suche nach Teilwörtern
            for part in keyword_parts:
                if len(part) > 3:
                    for word in words:
                        if part in word and word != part:
                            variations.add(word)
        else:
            # Suche nach ähnlichen Wörtern
            for word in words:
                if keyword in word and word != keyword:
                    variations.add(word)
                elif word in keyword and len(word) > 3:
                    variations.add(word)
        
        return list(variations)[:10]  # Limitiere auf 10
    
    def _find_related_keywords(self, words: List[str], main_keyword: str) -> List[Dict]:
        """
        Finde verwandte/semantische Keywords
        
        Args:
            words: Wortliste
            main_keyword: Haupt-Keyword
            
        Returns:
            Liste verwandter Keywords mit Häufigkeit
        """
        # Zähle Wörter
        word_counts = Counter(words)
        
        # Entferne Stopwörter
        stopwords = self._get_stopwords()
        
        # Filtere und sortiere
        related = []
        for word, count in word_counts.most_common(50):
            # Überspringe Stopwörter und Haupt-Keyword
            if word in stopwords or word == main_keyword.lower():
                continue
            
            # Nur Wörter mit mindestens 2 Vorkommen
            if count >= 2:
                related.append({
                    'keyword': word,
                    'count': count,
                    'relevance': self._calculate_relevance(word, main_keyword)
                })
        
        # Sortiere nach Relevanz
        related.sort(key=lambda x: x['relevance'], reverse=True)
        
        return related[:20]  # Top 20
    
    def _calculate_relevance(self, word: str, main_keyword: str) -> float:
        """
        Berechne Relevanz eines Wortes zum Haupt-Keyword
        
        Args:
            word: Zu bewertendes Wort
            main_keyword: Haupt-Keyword
            
        Returns:
            Relevanz-Score (0-1)
        """
        # Einfache Heuristik basierend auf String-Ähnlichkeit
        main_kw_lower = main_keyword.lower()
        
        # Exakte Übereinstimmung mit Keyword-Teil
        if word in main_kw_lower or main_kw_lower in word:
            return 1.0
        
        # Gemeinsame Zeichen
        common_chars = set(word) & set(main_kw_lower)
        similarity = len(common_chars) / max(len(word), len(main_kw_lower))
        
        return similarity
    
    def _find_keyword_positions(self, text: str, keyword: str) -> Dict:
        """
        Finde Positionen des Keywords im Text
        
        Args:
            text: Text
            keyword: Keyword
            
        Returns:
            Positions-Informationen
        """
        text_lower = text.lower()
        keyword_lower = keyword.lower()
        
        # Finde alle Positionen
        positions = []
        start = 0
        while True:
            pos = text_lower.find(keyword_lower, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1
        
        # Analysiere Verteilung
        text_length = len(text)
        
        in_first_100 = any(pos < 100 for pos in positions)
        in_first_paragraph = any(pos < 500 for pos in positions)
        in_last_paragraph = any(pos > text_length - 500 for pos in positions)
        
        return {
            'total_occurrences': len(positions),
            'in_first_100_chars': in_first_100,
            'in_first_paragraph': in_first_paragraph,
            'in_last_paragraph': in_last_paragraph,
            'positions': positions[:10]  # Erste 10 Positionen
        }
    
    def _get_stopwords(self) -> set:
        """Hole deutsche Stopwörter"""
        return {
            'der', 'die', 'das', 'den', 'dem', 'des', 'ein', 'eine', 'einer', 'eines',
            'und', 'oder', 'aber', 'ist', 'sind', 'war', 'waren', 'wird', 'werden',
            'hat', 'haben', 'hatte', 'hatten', 'kann', 'können', 'konnte', 'konnten',
            'muss', 'müssen', 'musste', 'mussten', 'soll', 'sollen', 'sollte', 'sollten',
            'für', 'mit', 'auf', 'bei', 'von', 'zu', 'im', 'am', 'an', 'als', 'auch',
            'nicht', 'nur', 'noch', 'mehr', 'sehr', 'wie', 'was', 'wenn', 'dass', 'weil',
            'sich', 'sie', 'er', 'es', 'wir', 'ihr', 'ich', 'du', 'man', 'diese', 'sein',
            'dieser', 'dieses', 'alle', 'jede', 'jeder', 'jedes', 'nach', 'über', 'vor',
            'aus', 'durch', 'um', 'bis', 'zum', 'zur', 'beim', 'vom', 'ins', 'ans',
            'gegen', 'ohne', 'seit', 'während', 'wegen', 'trotz', 'statt', 'außer',
            'hier', 'da', 'dort', 'dann', 'nun', 'schon', 'noch', 'immer', 'nie',
            'heute', 'morgen', 'gestern', 'jetzt', 'bald', 'oft', 'manchmal', 'immer'
        }
