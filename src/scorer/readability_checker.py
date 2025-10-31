"""
Readability Checker - Prüft Lesbarkeit von Texten
"""

import re
from typing import Dict


class ReadabilityChecker:
    """Prüft und bewertet Lesbarkeit von Texten"""
    
    def __init__(self, config):
        """
        Initialisiere Readability Checker
        
        Args:
            config: Config-Objekt
        """
        self.config = config
    
    def check(self, text: str) -> Dict:
        """
        Prüfe Lesbarkeit des Textes
        
        Args:
            text: Zu prüfender Text
            
        Returns:
            Lesbarkeits-Metriken
        """
        # Basis-Metriken
        sentences = self._split_sentences(text)
        words = self._split_words(text)
        syllables = self._count_syllables(text)
        
        # Berechne Metriken
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        avg_word_length = sum(len(w) for w in words) / len(words) if words else 0
        avg_syllables_per_word = syllables / len(words) if words else 0
        
        # Flesch Reading Ease (angepasst für Deutsch)
        flesch = self._calculate_flesch_reading_ease(
            len(sentences),
            len(words),
            syllables
        )
        
        # Komplexitäts-Score
        complexity = self._calculate_complexity(words, sentences)
        
        return {
            'flesch_reading_ease': round(flesch, 2),
            'avg_sentence_length': round(avg_sentence_length, 2),
            'avg_word_length': round(avg_word_length, 2),
            'avg_syllables_per_word': round(avg_syllables_per_word, 2),
            'total_sentences': len(sentences),
            'total_words': len(words),
            'total_syllables': syllables,
            'complexity_score': round(complexity, 2),
            'readability_grade': self._get_readability_grade(flesch)
        }
    
    def _split_sentences(self, text: str) -> list:
        """
        Teile Text in Sätze
        
        Args:
            text: Text
            
        Returns:
            Liste von Sätzen
        """
        # Einfache Satz-Trennung
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    def _split_words(self, text: str) -> list:
        """
        Teile Text in Wörter
        
        Args:
            text: Text
            
        Returns:
            Liste von Wörtern
        """
        # Entferne Sonderzeichen und teile
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        words = [w for w in words if w.strip()]
        return words
    
    def _count_syllables(self, text: str) -> int:
        """
        Zähle Silben im Text (vereinfachte deutsche Silbenzählung)
        
        Args:
            text: Text
            
        Returns:
            Anzahl Silben
        """
        words = self._split_words(text)
        total_syllables = 0
        
        for word in words:
            total_syllables += self._count_word_syllables(word.lower())
        
        return total_syllables
    
    def _count_word_syllables(self, word: str) -> int:
        """
        Zähle Silben in einem Wort (vereinfacht für Deutsch)
        
        Args:
            word: Wort
            
        Returns:
            Anzahl Silben
        """
        # Vereinfachte Silbenzählung für Deutsch
        # Zähle Vokale und Vokalgruppen
        vowels = 'aeiouäöüy'
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Mindestens 1 Silbe pro Wort
        return max(1, syllable_count)
    
    def _calculate_flesch_reading_ease(self, sentences: int, words: int, syllables: int) -> float:
        """
        Berechne Flesch Reading Ease Score (angepasst für Deutsch)
        
        Args:
            sentences: Anzahl Sätze
            words: Anzahl Wörter
            syllables: Anzahl Silben
            
        Returns:
            Flesch Score (0-100, höher = leichter lesbar)
        """
        if sentences == 0 or words == 0:
            return 0
        
        # Formel für deutsche Texte (Wiener Sachtextformel adaptiert)
        asl = words / sentences  # Average Sentence Length
        asw = syllables / words  # Average Syllables per Word
        
        # Angepasste Flesch-Formel für Deutsch
        score = 180 - asl - (58.5 * asw)
        
        # Normalisiere auf 0-100
        return max(0, min(100, score))
    
    def _calculate_complexity(self, words: list, sentences: list) -> float:
        """
        Berechne Komplexitäts-Score
        
        Args:
            words: Wortliste
            sentences: Satzliste
            
        Returns:
            Komplexitäts-Score (0-100, höher = komplexer)
        """
        if not words:
            return 0
        
        complexity = 0
        
        # Lange Wörter (> 12 Zeichen)
        long_words = sum(1 for w in words if len(w) > 12)
        long_word_ratio = long_words / len(words)
        complexity += long_word_ratio * 40
        
        # Lange Sätze (> 25 Wörter)
        if sentences:
            avg_sentence_length = len(words) / len(sentences)
            if avg_sentence_length > 25:
                complexity += 30
            elif avg_sentence_length > 20:
                complexity += 20
            elif avg_sentence_length > 15:
                complexity += 10
        
        # Wort-Diversität (viele unique Wörter = komplexer)
        unique_ratio = len(set(words)) / len(words)
        if unique_ratio > 0.7:
            complexity += 30
        elif unique_ratio > 0.5:
            complexity += 20
        
        return min(100, complexity)
    
    def _get_readability_grade(self, flesch_score: float) -> str:
        """
        Konvertiere Flesch Score zu Lesbarkeits-Grade
        
        Args:
            flesch_score: Flesch Reading Ease Score
            
        Returns:
            Lesbarkeits-Bewertung
        """
        if flesch_score >= 80:
            return "Sehr leicht (5. Klasse)"
        elif flesch_score >= 70:
            return "Leicht (6. Klasse)"
        elif flesch_score >= 60:
            return "Relativ leicht (7.-8. Klasse)"
        elif flesch_score >= 50:
            return "Standard (9.-10. Klasse)"
        elif flesch_score >= 40:
            return "Relativ schwierig (11.-12. Klasse)"
        elif flesch_score >= 30:
            return "Schwierig (Studium)"
        else:
            return "Sehr schwierig (Akademisch)"
