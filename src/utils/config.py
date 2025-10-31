"""
Konfigurationsmanagement für den SEO Content Generator
"""

import json
from pathlib import Path
from typing import Any, Optional


class Config:
    """Konfigurationsklasse für zentrale Einstellungsverwaltung"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialisiere Konfiguration
        
        Args:
            config_path: Pfad zur Konfigurationsdatei
        """
        self.config_path = Path(config_path)
        self.config_data = self._load_config()
    
    def _load_config(self) -> dict:
        """Lade Konfiguration aus Datei"""
        if not self.config_path.exists():
            # Fallback auf example config
            example_path = Path("config.example.json")
            if example_path.exists():
                print(f"⚠️  config.json nicht gefunden, verwende {example_path}")
                return json.loads(example_path.read_text(encoding="utf-8"))
            else:
                raise FileNotFoundError(
                    f"Konfigurationsdatei nicht gefunden: {self.config_path}\n"
                    "Bitte erstelle config.json basierend auf config.example.json"
                )
        
        return json.loads(self.config_path.read_text(encoding="utf-8"))
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Hole Konfigurationswert mit Punkt-Notation
        
        Args:
            key: Schlüssel in Punkt-Notation (z.B. "api_keys.openai")
            default: Standardwert falls Schlüssel nicht existiert
            
        Returns:
            Konfigurationswert oder default
        """
        keys = key.split(".")
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Setze Konfigurationswert mit Punkt-Notation
        
        Args:
            key: Schlüssel in Punkt-Notation
            value: Zu setzender Wert
        """
        keys = key.split(".")
        data = self.config_data
        
        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]
        
        data[keys[-1]] = value
    
    def save(self) -> None:
        """Speichere Konfiguration zurück in Datei"""
        self.config_path.write_text(
            json.dumps(self.config_data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    
    def get_content_type_config(self, content_type: str) -> dict:
        """
        Hole Konfiguration für spezifischen Content-Typ
        
        Args:
            content_type: Art des Contents (blog, produktbeschreibung, etc.)
            
        Returns:
            Content-Type spezifische Konfiguration
        """
        content_types = self.get("content_types", {})
        return content_types.get(content_type, content_types.get("blog", {}))
    
    def __getitem__(self, key: str) -> Any:
        """Ermöglicht config["key"] Zugriff"""
        return self.get(key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Ermöglicht config["key"] = value Zugriff"""
        self.set(key, value)
