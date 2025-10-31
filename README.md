# SEO Content Generator 🚀

Ein professionelles Python-basiertes Tool zur automatischen Generierung von SEO-optimierten deutschen Texten mit KI-Unterstützung.

## 🎯 Features

- **Automatische Konkurrenzanalyse**: Analysiert die Top 5 Google.de Rankings für dein Keyword
- **Content Scoring**: Berechnet Content Scores basierend auf SISTRIX-Metriken (Sichtbarkeitsindex, Keyword-Rankings, Content-Qualität)
- **KI-gestützte Textgenerierung**: Erstellt optimierte Texte (800-1200 Wörter) mit professionell-lockerer Tonalität
- **Automatische Bildgenerierung**: Generiert passende Bilder mit SEO-optimierten Alt- und Title-Tags
- **Interaktive Optimierung**: Feedback-Schleifen zur kontinuierlichen Verbesserung bis zum Ziel-Score (75-90+)
- **Multi-Content-Type Support**: Produktbeschreibungen, Kategorie-Texte, Ratgeber, How-to-Guides, Vergleichsartikel
- **HTML/Bootstrap 4 Output**: Responsive HTML-Ausgabe mit vollständigen Meta-Daten
- **Report-System**: Automatische Dashboards und Analyse-Reports
- **GitHub-Integration**: Versionierung und History-Tracking

## 📊 Content Score Metriken

Das System bewertet Texte anhand folgender Kriterien:

1. **Keyword-Optimierung** (20%)
   - Haupt-Keyword Dichte
   - LSI/Semantische Keywords
   - Keyword-Platzierung

2. **Struktur & Lesbarkeit** (25%)
   - Überschriftenstruktur (H1-H6)
   - Absatzlänge und -struktur
   - Flesch-Reading-Score
   - Aufzählungen und Listen

3. **Content-Qualität** (30%)
   - Textlänge vs. Konkurrenz
   - Informationstiefe
   - Unique Content
   - Themenrelevanz

4. **Technisches SEO** (15%)
   - Meta-Title Optimierung
   - Meta-Description
   - Alt-Tags für Bilder
   - HTML-Struktur

5. **Engagement-Faktoren** (10%)
   - Call-to-Actions
   - Multimediale Elemente
   - Interne Struktur

## 🚀 Installation

```bash
# Repository klonen
git clone https://github.com/mrhanf15-stack/seo-content-generator.git
cd seo-content-generator

# Virtuelle Umgebung erstellen
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate  # Windows

# Dependencies installieren
pip install -r requirements.txt

# Konfiguration anpassen
cp config.example.json config.json
# API-Keys in config.json eintragen
```

## 💻 Verwendung

### Einfacher Modus

```bash
python main.py --keyword "dein keyword" --type "blog"
```

### Interaktiver Modus

```bash
python main.py --interactive
```

### Mit erweiterten Optionen

```bash
python main.py \
  --keyword "seo texte schreiben" \
  --type "ratgeber" \
  --target-score 85 \
  --word-count 1200 \
  --generate-images 3
```

## 📁 Projektstruktur

```
seo-content-generator/
├── src/
│   ├── analyzer/          # Konkurrenzanalyse-Module
│   │   ├── google_scraper.py
│   │   ├── content_extractor.py
│   │   └── competitor_analyzer.py
│   ├── generator/         # Text- und Bild-Generierung
│   │   ├── text_generator.py
│   │   ├── image_generator.py
│   │   └── meta_generator.py
│   ├── scorer/           # Content Scoring System
│   │   ├── content_scorer.py
│   │   ├── keyword_analyzer.py
│   │   └── readability_checker.py
│   └── utils/            # Hilfsfunktionen
│       ├── config.py
│       ├── logger.py
│       └── html_builder.py
├── data/
│   ├── templates/        # HTML-Templates
│   ├── outputs/          # Generierte Inhalte
│   └── history/          # Analyse-Historie (JSON)
├── docs/                 # Dokumentation
├── tests/                # Unit Tests
├── main.py              # Hauptprogramm
├── requirements.txt     # Python Dependencies
└── config.json          # Konfiguration
```

## 🔧 Konfiguration

Die `config.json` enthält alle wichtigen Einstellungen:

```json
{
  "api_keys": {
    "openai": "your-api-key",
    "image_generator": "your-api-key"
  },
  "scoring": {
    "target_score": 75,
    "max_iterations": 5
  },
  "content": {
    "language": "de",
    "word_count_min": 800,
    "word_count_max": 1200,
    "tone": "professional-casual"
  }
}
```

## 📈 Workflow

1. **Keyword eingeben**: Gib dein Ziel-Keyword ein
2. **Konkurrenzanalyse**: System analysiert Top 5 Google-Rankings
3. **Erstentwurf**: KI generiert ersten Text-Entwurf
4. **Scoring**: Content Score wird berechnet
5. **Optimierung**: Iterative Verbesserung bis Ziel-Score erreicht
6. **Bildgenerierung**: Passende Bilder werden erstellt
7. **Output**: HTML-Datei mit vollständigen Meta-Daten
8. **Report**: Dashboard mit Analyse-Ergebnissen

## 🎨 Content-Typen

- **Blog-Artikel**: Informative Ratgeber und How-to-Guides
- **Produktbeschreibungen**: Verkaufsorientierte E-Commerce-Texte
- **Kategorie-Texte**: SEO-Texte für Shop-Kategorien
- **Vergleichsartikel**: Produkt- und Dienstleistungsvergleiche
- **Landing Pages**: Conversion-optimierte Seiten

## 📊 Reports & Analytics

Das System generiert automatisch:

- **Content Score Dashboard**: Visualisierung aller Metriken
- **Konkurrenz-Vergleich**: Benchmarking gegen Top 5
- **Optimierungs-Historie**: Tracking der Verbesserungen
- **Keyword-Analyse**: Semantische Keyword-Übersicht
- **Export-Optionen**: PDF und HTML-Reports

## 🤝 Contributing

Contributions sind willkommen! Bitte erstelle einen Pull Request oder öffne ein Issue.

## 📝 Lizenz

MIT License - siehe [LICENSE](LICENSE) Datei

## 👨‍💻 Autor

Entwickelt mit ❤️ für professionelle SEO-Content-Erstellung

## 🔗 Links

- [Dokumentation](docs/)
- [Issues](https://github.com/mrhanf15-stack/seo-content-generator/issues)
- [Changelog](CHANGELOG.md)

---

**Version**: 1.0.0  
**Status**: In Entwicklung 🚧
