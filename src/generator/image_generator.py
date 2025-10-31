"""
Image Generator - Generiert Bilder mit KI und erstellt SEO-Tags
"""

import os
from typing import List, Dict
from pathlib import Path
from openai import OpenAI
import requests
from datetime import datetime
from slugify import slugify
from src.utils.logger import get_logger


class ImageGenerator:
    """Generiert Bilder mit KI und SEO-optimierten Tags"""
    
    def __init__(self, config):
        """
        Initialisiere Image Generator
        
        Args:
            config: Config-Objekt
        """
        self.config = config
        self.logger = get_logger()
        
        # OpenAI Client
        api_key = os.getenv('OPENAI_API_KEY') or config.get("api_keys.openai")
        self.client = OpenAI(api_key=api_key)
        
        # Image Settings
        self.model = config.get("api_keys.image_generator", "dall-e-3")
        self.size = config.get("images.size", "1792x1024")
        self.quality = config.get("images.quality", "standard")
        self.style = config.get("images.style", "natural")
    
    def generate(self, keyword: str, text: str, content_type: str, count: int = 3) -> List[Dict]:
        """
        Generiere Bilder für Content
        
        Args:
            keyword: Haupt-Keyword
            text: Content-Text
            content_type: Content-Typ
            count: Anzahl zu generierender Bilder
            
        Returns:
            Liste mit Bild-Daten (path, url, alt, title)
        """
        if not self.config.get("images.generate", True):
            self.logger.info("Bild-Generierung deaktiviert")
            return []
        
        self.logger.info(f"Generiere {count} Bilder für '{keyword}'")
        
        images = []
        
        for i in range(count):
            try:
                # Erstelle Prompt für Bild
                prompt = self._build_image_prompt(keyword, content_type, i + 1, count)
                
                # Generiere Bild
                image_data = self._generate_single_image(prompt, keyword, i + 1)
                
                if image_data:
                    images.append(image_data)
                    self.logger.info(f"✓ Bild {i+1}/{count} generiert")
                
            except Exception as e:
                self.logger.error(f"Fehler bei Bild {i+1}: {e}")
                continue
        
        self.logger.info(f"✓ {len(images)} Bilder erfolgreich generiert")
        
        return images
    
    def _build_image_prompt(self, keyword: str, content_type: str, number: int, total: int) -> str:
        """
        Erstelle Prompt für Bild-Generierung
        
        Args:
            keyword: Keyword
            content_type: Content-Typ
            number: Bild-Nummer
            total: Gesamt-Anzahl
            
        Returns:
            Bild-Prompt
        """
        # Basis-Stil
        style = "professional, clean, modern, high-quality"
        
        # Content-Type spezifische Anpassungen
        if content_type == "produktbeschreibung":
            style += ", product photography, commercial"
        elif content_type == "blog":
            style += ", editorial, informative"
        elif content_type == "ratgeber":
            style += ", educational, illustrative"
        
        # Verschiedene Perspektiven für mehrere Bilder
        perspectives = [
            "hero image, wide angle",
            "close-up detail shot",
            "overview composition",
            "lifestyle context",
            "technical diagram style"
        ]
        
        perspective = perspectives[(number - 1) % len(perspectives)]
        
        prompt = f"""A {style} image about {keyword}. {perspective}. 
Professional photography, well-lit, sharp focus, suitable for web content.
No text or watermarks in the image."""
        
        return prompt
    
    def _generate_single_image(self, prompt: str, keyword: str, number: int) -> Dict:
        """
        Generiere einzelnes Bild
        
        Args:
            prompt: Bild-Prompt
            keyword: Keyword
            number: Bild-Nummer
            
        Returns:
            Bild-Daten
        """
        try:
            # Generiere mit DALL-E
            response = self.client.images.generate(
                model=self.model,
                prompt=prompt,
                size=self.size,
                quality=self.quality,
                n=1
            )
            
            # Hole Image URL
            image_url = response.data[0].url
            
            # Download Bild
            local_path = self._download_image(image_url, keyword, number)
            
            # Generiere SEO-Tags
            alt_tag = self._generate_alt_tag(keyword, number)
            title_tag = self._generate_title_tag(keyword, number)
            
            return {
                'path': str(local_path),
                'url': image_url,
                'alt': alt_tag,
                'title': title_tag,
                'number': number
            }
            
        except Exception as e:
            self.logger.error(f"Fehler bei Bild-Generierung: {e}")
            return None
    
    def _download_image(self, url: str, keyword: str, number: int) -> Path:
        """
        Download Bild von URL
        
        Args:
            url: Bild-URL
            keyword: Keyword
            number: Bild-Nummer
            
        Returns:
            Lokaler Pfad
        """
        # Erstelle Dateinamen
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = slugify(keyword)
        filename = f"{slug}_{number}_{timestamp}.png"
        
        # Speicher-Pfad
        output_dir = Path("data/outputs/images")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = output_dir / filename
        
        # Download
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        filepath.write_bytes(response.content)
        
        return filepath
    
    def _generate_alt_tag(self, keyword: str, number: int) -> str:
        """
        Generiere Alt-Tag für Bild
        
        Args:
            keyword: Keyword
            number: Bild-Nummer
            
        Returns:
            Alt-Tag
        """
        variations = [
            f"{keyword} - Übersicht und Informationen",
            f"{keyword} im Detail",
            f"Alles über {keyword}",
            f"{keyword} - Ratgeber und Tipps",
            f"{keyword} erklärt"
        ]
        
        return variations[(number - 1) % len(variations)]
    
    def _generate_title_tag(self, keyword: str, number: int) -> str:
        """
        Generiere Title-Tag für Bild
        
        Args:
            keyword: Keyword
            number: Bild-Nummer
            
        Returns:
            Title-Tag
        """
        variations = [
            f"{keyword} | Professioneller Ratgeber",
            f"{keyword} | Detaillierte Informationen",
            f"{keyword} | Expertenwissen",
            f"{keyword} | Umfassender Guide",
            f"{keyword} | Alle Fakten"
        ]
        
        return variations[(number - 1) % len(variations)]
