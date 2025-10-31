"""
Meta Generator - Generiert SEO Meta-Daten (Title, Description, H1)
"""

import os
from typing import Dict
from openai import OpenAI
from src.utils.logger import get_logger


class MetaGenerator:
    """Generiert SEO-optimierte Meta-Daten"""
    
    def __init__(self, config):
        """
        Initialisiere Meta Generator
        
        Args:
            config: Config-Objekt
        """
        self.config = config
        self.logger = get_logger()
        
        # OpenAI Client
        api_key = os.getenv('OPENAI_API_KEY') or config.get("api_keys.openai")
        self.client = OpenAI(api_key=api_key)
        self.model = config.get("api_keys.openai_model", "gpt-4.1-mini")
    
    def generate(self, text: str, keyword: str, content_type: str) -> Dict[str, str]:
        """
        Generiere Meta-Daten für Text
        
        Args:
            text: Haupt-Content
            keyword: Haupt-Keyword
            content_type: Content-Typ
            
        Returns:
            Dictionary mit Meta-Daten (title, description, h1)
        """
        self.logger.info(f"Generiere Meta-Daten für '{keyword}'")
        
        # Erstelle Prompt
        prompt = self._build_meta_prompt(text, keyword, content_type)
        
        # Generiere Meta-Daten
        meta_text = self._call_openai(prompt)
        
        # Parse Ergebnis
        meta_data = self._parse_meta_response(meta_text, keyword)
        
        self.logger.info("✓ Meta-Daten generiert")
        
        return meta_data
    
    def _build_meta_prompt(self, text: str, keyword: str, content_type: str) -> str:
        """
        Erstelle Prompt für Meta-Generierung
        
        Args:
            text: Content-Text
            keyword: Keyword
            content_type: Content-Typ
            
        Returns:
            Prompt
        """
        # Kürze Text für Prompt (erste 500 Wörter)
        text_preview = ' '.join(text.split()[:500])
        
        prompt = f"""Du bist ein SEO-Experte. Erstelle optimierte Meta-Daten für folgenden Text.

**Haupt-Keyword:** {keyword}
**Content-Typ:** {content_type}

**Text-Vorschau:**
{text_preview}

**Anforderungen:**

1. **SEO-Title:**
   - 50-60 Zeichen
   - Keyword am Anfang
   - Ansprechend und klickstark
   - Format: "Keyword | Zusatzinfo" oder "Keyword: Nutzen"

2. **Meta-Description:**
   - 140-160 Zeichen
   - Keyword enthalten
   - Call-to-Action
   - Mehrwert kommunizieren
   - Zum Klicken animieren

3. **H1-Überschrift:**
   - 40-70 Zeichen
   - Keyword enthalten
   - Klar und prägnant
   - Neugier wecken

**Format der Antwort:**
Gib die Meta-Daten in folgendem Format zurück:

TITLE: [Dein SEO-Title hier]
DESCRIPTION: [Deine Meta-Description hier]
H1: [Deine H1-Überschrift hier]

Erstelle jetzt die Meta-Daten:"""
        
        return prompt
    
    def _parse_meta_response(self, response: str, keyword: str) -> Dict[str, str]:
        """
        Parse Meta-Daten aus API-Response
        
        Args:
            response: API-Response
            keyword: Keyword (Fallback)
            
        Returns:
            Geparste Meta-Daten
        """
        meta_data = {
            'title': '',
            'description': '',
            'h1': ''
        }
        
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('TITLE:'):
                meta_data['title'] = line.replace('TITLE:', '').strip()
            elif line.startswith('DESCRIPTION:'):
                meta_data['description'] = line.replace('DESCRIPTION:', '').strip()
            elif line.startswith('H1:'):
                meta_data['h1'] = line.replace('H1:', '').strip()
        
        # Fallbacks falls Parsing fehlschlägt
        if not meta_data['title']:
            meta_data['title'] = f"{keyword} | Ratgeber & Tipps"
        if not meta_data['description']:
            meta_data['description'] = f"Alles über {keyword} ✓ Ausführlicher Ratgeber ✓ Tipps & Tricks ✓ Jetzt informieren!"
        if not meta_data['h1']:
            meta_data['h1'] = keyword
        
        # Validiere Längen
        meta_data = self._validate_meta_lengths(meta_data, keyword)
        
        return meta_data
    
    def _validate_meta_lengths(self, meta_data: Dict[str, str], keyword: str) -> Dict[str, str]:
        """
        Validiere und korrigiere Meta-Daten Längen
        
        Args:
            meta_data: Meta-Daten
            keyword: Keyword
            
        Returns:
            Validierte Meta-Daten
        """
        # Title: 50-60 Zeichen
        if len(meta_data['title']) > 60:
            meta_data['title'] = meta_data['title'][:57] + '...'
            self.logger.warning("Title zu lang, gekürzt")
        elif len(meta_data['title']) < 50:
            if len(meta_data['title']) < 40:
                meta_data['title'] = f"{meta_data['title']} | Ratgeber"
        
        # Description: 140-160 Zeichen
        if len(meta_data['description']) > 160:
            meta_data['description'] = meta_data['description'][:157] + '...'
            self.logger.warning("Description zu lang, gekürzt")
        elif len(meta_data['description']) < 140:
            if len(meta_data['description']) < 120:
                meta_data['description'] += " Jetzt mehr erfahren!"
        
        # H1: 40-70 Zeichen
        if len(meta_data['h1']) > 70:
            meta_data['h1'] = meta_data['h1'][:67] + '...'
        elif len(meta_data['h1']) < 40:
            if len(meta_data['h1']) < 30:
                meta_data['h1'] = f"{meta_data['h1']} - Der ultimative Guide"
        
        return meta_data
    
    def _call_openai(self, prompt: str) -> str:
        """
        Rufe OpenAI API auf
        
        Args:
            prompt: Prompt
            
        Returns:
            Response-Text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Du bist ein SEO-Experte spezialisiert auf Meta-Daten Optimierung für deutsche Websites."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"Fehler bei OpenAI API-Aufruf: {e}")
            raise
