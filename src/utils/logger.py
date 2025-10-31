"""
Logging-Konfiguration für den SEO Content Generator
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logger(config, name: str = "seo_generator") -> logging.Logger:
    """
    Richte Logger ein mit Konsolen- und Datei-Output
    
    Args:
        config: Config-Objekt
        name: Logger-Name
        
    Returns:
        Konfigurierter Logger
    """
    logger = logging.getLogger(name)
    
    # Level aus Config
    level_str = config.get("logging.level", "INFO")
    level = getattr(logging, level_str.upper(), logging.INFO)
    logger.setLevel(level)
    
    # Verhindere doppelte Handler
    if logger.handlers:
        return logger
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Konsolen-Handler
    if config.get("logging.console", True):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Datei-Handler
    log_file = config.get("logging.file", "logs/seo_generator.log")
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "seo_generator") -> logging.Logger:
    """
    Hole existierenden Logger
    
    Args:
        name: Logger-Name
        
    Returns:
        Logger-Instanz
    """
    return logging.getLogger(name)
