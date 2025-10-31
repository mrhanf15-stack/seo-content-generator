"""
Text Generator - KI-gestützte Textgenerierung mit OpenAI
"""

import os
from typing import Dict, List, Optional
from openai import OpenAI
from src.utils.logger import get_logger


class TextGenerator:
    """Generiert SEO-optimierte Texte mit KI-Unterstützung"""
    
    def __init__(self, config):
        """
        Initialisiere Text Generator
        
        Args:
            config: Config-Objekt
        """
        self.config = config
        self.logger = get_logger()
        
        # OpenAI Client initialisieren
        api_key = os.getenv('OPENAI_API_KEY') or config.get("api_keys.openai")
        if not api_key:
            raise ValueError("OpenAI API Key nicht gefunden. Bitte in config.json oder als OPENAI_API_KEY Umgebungsvariable setzen.")
        
        self.client = OpenAI(api_key=api_key)
        self.model = config.get("api_keys.openai_model", "gpt-4.1-mini")
    
    def generate(self, params: Dict) -> str:
        """
        Generiere SEO-optimierten Text
        
        Args:
            params: Generierungs-Parameter (keyword, content_type, competitor_data, etc.)
            
        Returns:
            Generierter Text
        """
        keyword = params['keyword']
        content_type = params['content_type']
        competitor_data = params.get('competitor_data', {})
        word_count = params.get('word_count', 1000)
        
        self.logger.info(f"Generiere Text für '{keyword}' (Typ: {content_type}, Länge: {word_count} Wörter)")
        
        # Erstelle Prompt
        prompt = self._build_generation_prompt(keyword, content_type, competitor_data, word_count)
        
        # Generiere Text
        text = self._call_openai(prompt, max_tokens=3000)
        
        self.logger.info(f"✓ Text generiert ({len(text.split())} Wörter)")
        
        return text
    
    def optimize(self, text: str, suggestions: List[str], params: Dict) -> str:
        """
        Optimiere bestehenden Text basierend auf Vorschlägen
        
        Args:
            text: Zu optimierender Text
            suggestions: Verbesserungsvorschläge
            params: Generierungs-Parameter
            
        Returns:
            Optimierter Text
        """
        keyword = params['keyword']
        
        self.logger.info(f"Optimiere Text mit {len(suggestions)} Vorschlägen")
        
        # Erstelle Optimierungs-Prompt
        prompt = self._build_optimization_prompt(text, suggestions, keyword)
        
        # Optimiere
        optimized_text = self._call_openai(prompt, max_tokens=3500)
        
        self.logger.info("✓ Text optimiert")
        
        return optimized_text
    
    def _build_generation_prompt(self, keyword: str, content_type: str, competitor_data: Dict, word_count: int) -> str:
        """
        Erstelle Prompt für Text-Generierung
        
        Args:
            keyword: Haupt-Keyword
            content_type: Content-Typ
            competitor_data: Konkurrenz-Daten
            word_count: Ziel-Wortanzahl
            
        Returns:
            Generierungs-Prompt
        """
        # Hole Content-Type Config
        type_config = self.config.get_content_type_config(content_type)
        
        # Extrahiere Insights
        insights = competitor_data.get('insights', {})
        common_topics = insights.get('common_topics', [])
        benchmarks = competitor_data.get('benchmarks', {})
        
        # Empfohlene Struktur
        recommended_h2 = insights.get('recommended_h2_count', 5)
        recommended_h3 = insights.get('recommended_h3_count', 3)
        
        prompt = f"""Du bist ein professioneller SEO-Texter für deutsche Texte. Erstelle einen hochwertigen, SEO-optimierten Text.

**Haupt-Keyword:** {keyword}

**Content-Typ:** {type_config.get('description', content_type)}
**Ziel-Wortanzahl:** {word_count} Wörter
**Tonalität:** Professionell-locker, persönliche "Du"-Anrede wo passend

**SEO-Anforderungen:**
- Keyword-Dichte: 1-3%
- Keyword im ersten Absatz und in Überschriften
- {recommended_h2} H2-Überschriften
- {recommended_h3} H3-Überschriften
- Kurze Sätze (max. 20 Wörter durchschnittlich)
- Gut strukturierte Absätze (max. 100 Wörter)
- Listen und Aufzählungen verwenden

**Wichtige Themen (aus Konkurrenzanalyse):**
{', '.join(common_topics[:10]) if common_topics else 'Keine spezifischen Themen'}

**Struktur-Vorgaben:**
{self._get_structure_guidelines(type_config)}

**Inhaltliche Anforderungen:**
- Informativ und hilfreich
- Faktenbasiert mit konkreten Informationen
- Keine medizinischen Heilversprechen
- Keine Slang-Begriffe
- Professionelle Darstellung
- Mehrwert für den Leser

**Format:**
- Schreibe in Plain Text (kein HTML)
- Verwende Markdown für Formatierung
- Strukturiere mit # für H1, ## für H2, ### für H3
- Verwende **fett** für wichtige Begriffe
- Erstelle Listen mit - oder 1., 2., 3.

Schreibe jetzt den vollständigen Text:"""
        
        return prompt
    
    def _build_optimization_prompt(self, text: str, suggestions: List[str], keyword: str) -> str:
        """
        Erstelle Prompt für Text-Optimierung
        
        Args:
            text: Ursprünglicher Text
            suggestions: Verbesserungsvorschläge
            keyword: Haupt-Keyword
            
        Returns:
            Optimierungs-Prompt
        """
        suggestions_text = '\n'.join(f"- {s}" for s in suggestions[:10])
        
        prompt = f"""Du bist ein professioneller SEO-Texter. Optimiere den folgenden Text basierend auf den Verbesserungsvorschlägen.

**Haupt-Keyword:** {keyword}

**Verbesserungsvorschläge:**
{suggestions_text}

**Ursprünglicher Text:**
{text}

**Optimierungs-Richtlinien:**
- Behalte die Grundstruktur und den Inhalt bei
- Implementiere die Verbesserungsvorschläge
- Verbessere SEO-Optimierung (Keyword-Platzierung, Dichte)
- Optimiere Lesbarkeit und Struktur
- Füge fehlende Elemente hinzu (z.B. mehr H2/H3, Listen)
- Behalte die professionell-lockere Tonalität mit "Du"-Anrede
- Behalte Markdown-Formatierung bei

Schreibe jetzt den optimierten Text:"""
        
        return prompt
    
    def _get_structure_guidelines(self, type_config: Dict) -> str:
        """
        Hole Struktur-Richtlinien für Content-Typ
        
        Args:
            type_config: Content-Type Konfiguration
            
        Returns:
            Struktur-Beschreibung
        """
        structure = type_config.get('structure', [])
        focus = type_config.get('focus', 'information')
        cta_required = type_config.get('cta_required', False)
        
        guidelines = []
        
        if structure:
            guidelines.append(f"Strukturiere den Text in folgende Abschnitte: {', '.join(structure)}")
        
        if focus == 'conversion':
            guidelines.append("Fokus auf Conversion: Vorteile hervorheben, zum Handeln motivieren")
        elif focus == 'information':
            guidelines.append("Fokus auf Information: Ausführlich erklären, Mehrwert bieten")
        elif focus == 'education':
            guidelines.append("Fokus auf Bildung: Schritt-für-Schritt erklären, praktische Tipps")
        elif focus == 'comparison':
            guidelines.append("Fokus auf Vergleich: Objektiv vergleichen, Vor-/Nachteile aufzeigen")
        
        if cta_required:
            guidelines.append("Füge Call-to-Actions ein (z.B. 'Jetzt entdecken', 'Mehr erfahren')")
        
        return '\n'.join(f"- {g}" for g in guidelines) if guidelines else "Keine spezifischen Vorgaben"
    
    def _call_openai(self, prompt: str, max_tokens: int = 2000) -> str:
        """
        Rufe OpenAI API auf
        
        Args:
            prompt: Prompt-Text
            max_tokens: Maximale Token-Anzahl
            
        Returns:
            Generierter Text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Du bist ein professioneller SEO-Texter für deutsche Texte mit Expertise in Content-Marketing und Suchmaschinenoptimierung."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.7,
                top_p=0.9
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"Fehler bei OpenAI API-Aufruf: {e}")
            raise
