#!/usr/bin/env python3
"""
SEO Content Generator - Hauptprogramm
Automatische Generierung von SEO-optimierten deutschen Texten mit KI-Unterstützung
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional

from src.utils.config import Config
from src.utils.logger import setup_logger
from src.analyzer.competitor_analyzer import CompetitorAnalyzer
from src.scorer.content_scorer import ContentScorer
from src.generator.text_generator import TextGenerator
from src.generator.image_generator import ImageGenerator
from src.generator.meta_generator import MetaGenerator
from src.utils.html_builder import HTMLBuilder
from src.utils.report_generator import ReportGenerator


class SEOContentGenerator:
    """Hauptklasse für den SEO Content Generator"""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialisiere den Generator mit Konfiguration"""
        self.config = Config(config_path)
        self.logger = setup_logger(self.config)
        self.logger.info("SEO Content Generator gestartet")
        
        # Module initialisieren
        self.competitor_analyzer = CompetitorAnalyzer(self.config)
        self.content_scorer = ContentScorer(self.config)
        self.text_generator = TextGenerator(self.config)
        self.image_generator = ImageGenerator(self.config)
        self.meta_generator = MetaGenerator(self.config)
        self.html_builder = HTMLBuilder(self.config)
        self.report_generator = ReportGenerator(self.config)
    
    def generate_content(
        self,
        keyword: str,
        content_type: str = "blog",
        target_score: int = 75,
        word_count: Optional[int] = None,
        generate_images: bool = True,
        image_count: int = 3
    ) -> dict:
        """
        Generiere SEO-optimierten Content für ein Keyword
        
        Args:
            keyword: Ziel-Keyword
            content_type: Art des Contents (blog, produktbeschreibung, etc.)
            target_score: Ziel Content Score
            word_count: Gewünschte Wortanzahl (optional)
            generate_images: Bilder generieren
            image_count: Anzahl der zu generierenden Bilder
            
        Returns:
            dict: Ergebnis mit generiertem Content und Metriken
        """
        self.logger.info(f"Starte Content-Generierung für Keyword: '{keyword}'")
        
        # Phase 1: Konkurrenzanalyse
        self.logger.info("Phase 1: Analysiere Top 5 Google-Rankings...")
        competitor_data = self.competitor_analyzer.analyze(keyword)
        
        if not competitor_data or not competitor_data.get('competitors'):
            self.logger.error("Keine Konkurrenz-Daten gefunden")
            return {"success": False, "error": "Konkurrenzanalyse fehlgeschlagen"}
        
        self.logger.info(f"✓ {len(competitor_data['competitors'])} Konkurrenten analysiert")
        
        # Phase 2: Ersten Text-Entwurf generieren
        self.logger.info("Phase 2: Generiere ersten Text-Entwurf...")
        
        generation_params = {
            "keyword": keyword,
            "content_type": content_type,
            "competitor_data": competitor_data,
            "word_count": word_count or self.config.get("content.word_count_min", 1000)
        }
        
        draft_text = self.text_generator.generate(generation_params)
        self.logger.info(f"✓ Entwurf erstellt ({len(draft_text.split())} Wörter)")
        
        # Phase 3: Content Score berechnen
        self.logger.info("Phase 3: Berechne Content Score...")
        score_result = self.content_scorer.score(draft_text, keyword, competitor_data)
        current_score = score_result['total_score']
        self.logger.info(f"✓ Aktueller Score: {current_score}/100")
        
        # Phase 4: Iterative Optimierung
        iteration = 1
        max_iterations = self.config.get("scoring.max_iterations", 5)
        optimized_text = draft_text
        
        while current_score < target_score and iteration <= max_iterations:
            self.logger.info(f"Phase 4.{iteration}: Optimiere Text (Score: {current_score} → Ziel: {target_score})...")
            
            # Optimierungsvorschläge generieren
            suggestions = self.content_scorer.get_improvement_suggestions(score_result)
            
            # Text optimieren
            optimized_text = self.text_generator.optimize(
                optimized_text,
                suggestions,
                generation_params
            )
            
            # Neuen Score berechnen
            score_result = self.content_scorer.score(optimized_text, keyword, competitor_data)
            new_score = score_result['total_score']
            
            self.logger.info(f"✓ Score verbessert: {current_score} → {new_score}")
            
            if new_score <= current_score:
                self.logger.warning("Keine Verbesserung, breche Optimierung ab")
                break
            
            current_score = new_score
            iteration += 1
        
        # Phase 5: Meta-Daten generieren
        self.logger.info("Phase 5: Generiere Meta-Daten...")
        meta_data = self.meta_generator.generate(optimized_text, keyword, content_type)
        self.logger.info("✓ Meta-Daten erstellt (Title, Description, H1)")
        
        # Phase 6: Bilder generieren (optional)
        images = []
        if generate_images:
            self.logger.info(f"Phase 6: Generiere {image_count} Bilder...")
            images = self.image_generator.generate(
                keyword,
                optimized_text,
                content_type,
                count=image_count
            )
            self.logger.info(f"✓ {len(images)} Bilder generiert")
        
        # Phase 7: HTML-Output erstellen
        self.logger.info("Phase 7: Erstelle HTML-Output...")
        html_output = self.html_builder.build(
            text=optimized_text,
            meta_data=meta_data,
            images=images,
            keyword=keyword,
            content_type=content_type
        )
        
        # Speichern
        output_path = self._save_output(keyword, html_output, optimized_text, meta_data)
        self.logger.info(f"✓ Output gespeichert: {output_path}")
        
        # Phase 8: Report generieren
        self.logger.info("Phase 8: Generiere Report...")
        report = self.report_generator.generate(
            keyword=keyword,
            final_text=optimized_text,
            score_result=score_result,
            competitor_data=competitor_data,
            meta_data=meta_data,
            images=images,
            iterations=iteration - 1
        )
        
        report_path = self._save_report(keyword, report)
        self.logger.info(f"✓ Report gespeichert: {report_path}")
        
        # Ergebnis zusammenstellen
        result = {
            "success": True,
            "keyword": keyword,
            "content_type": content_type,
            "final_score": current_score,
            "target_score": target_score,
            "iterations": iteration - 1,
            "word_count": len(optimized_text.split()),
            "meta_data": meta_data,
            "images_generated": len(images),
            "output_path": str(output_path),
            "report_path": str(report_path),
            "score_breakdown": score_result
        }
        
        self.logger.info(f"✅ Content-Generierung abgeschlossen! Final Score: {current_score}/100")
        
        return result
    
    def _save_output(self, keyword: str, html: str, text: str, meta_data: dict) -> Path:
        """Speichere generierten Content"""
        from datetime import datetime
        from slugify import slugify
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = slugify(keyword)
        
        output_dir = Path("data/outputs") / f"{slug}_{timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # HTML speichern
        html_path = output_dir / "content.html"
        html_path.write_text(html, encoding="utf-8")
        
        # Markdown speichern
        md_path = output_dir / "content.md"
        md_path.write_text(text, encoding="utf-8")
        
        # Meta-Daten speichern
        meta_path = output_dir / "meta.json"
        meta_path.write_text(json.dumps(meta_data, ensure_ascii=False, indent=2), encoding="utf-8")
        
        return html_path
    
    def _save_report(self, keyword: str, report: dict) -> Path:
        """Speichere Report"""
        from datetime import datetime
        from slugify import slugify
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = slugify(keyword)
        
        # History speichern
        history_dir = Path("data/history")
        history_dir.mkdir(parents=True, exist_ok=True)
        
        history_path = history_dir / f"{slug}_{timestamp}.json"
        history_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        
        return history_path


def interactive_mode():
    """Interaktiver Modus mit Benutzerführung"""
    print("\n" + "="*60)
    print("🚀 SEO Content Generator - Interaktiver Modus")
    print("="*60 + "\n")
    
    # Keyword abfragen
    keyword = input("📝 Gib dein Ziel-Keyword ein: ").strip()
    if not keyword:
        print("❌ Keyword erforderlich!")
        return
    
    # Content-Typ auswählen
    print("\n📋 Wähle den Content-Typ:")
    print("1. Blog-Artikel / Ratgeber")
    print("2. Produktbeschreibung")
    print("3. Kategorie-Text")
    print("4. How-to-Guide")
    print("5. Vergleichsartikel")
    
    type_map = {
        "1": "blog",
        "2": "produktbeschreibung",
        "3": "kategorie",
        "4": "ratgeber",
        "5": "vergleich"
    }
    
    choice = input("\nDeine Wahl (1-5): ").strip()
    content_type = type_map.get(choice, "blog")
    
    # Ziel-Score
    target_input = input("\n🎯 Ziel Content Score (75-90+, Enter für 75): ").strip()
    target_score = int(target_input) if target_input.isdigit() else 75
    
    # Bilder generieren?
    gen_images = input("\n🖼️  Bilder generieren? (j/n, Enter für ja): ").strip().lower()
    generate_images = gen_images != "n"
    
    image_count = 3
    if generate_images:
        img_count_input = input("   Anzahl Bilder (1-5, Enter für 3): ").strip()
        image_count = int(img_count_input) if img_count_input.isdigit() else 3
    
    print("\n" + "="*60)
    print("⚙️  Starte Generierung...")
    print("="*60 + "\n")
    
    # Generator starten
    generator = SEOContentGenerator()
    result = generator.generate_content(
        keyword=keyword,
        content_type=content_type,
        target_score=target_score,
        generate_images=generate_images,
        image_count=image_count
    )
    
    # Ergebnis anzeigen
    if result["success"]:
        print("\n" + "="*60)
        print("✅ ERFOLGREICH ABGESCHLOSSEN!")
        print("="*60)
        print(f"\n📊 Final Score: {result['final_score']}/100")
        print(f"📝 Wortanzahl: {result['word_count']}")
        print(f"🔄 Optimierungs-Iterationen: {result['iterations']}")
        print(f"🖼️  Generierte Bilder: {result['images_generated']}")
        print(f"\n💾 Output: {result['output_path']}")
        print(f"📈 Report: {result['report_path']}")
        print("\n" + "="*60 + "\n")
    else:
        print(f"\n❌ Fehler: {result.get('error', 'Unbekannter Fehler')}\n")


def main():
    """Hauptfunktion"""
    parser = argparse.ArgumentParser(
        description="SEO Content Generator - Automatische Generierung von SEO-optimierten Texten"
    )
    
    parser.add_argument(
        "--keyword",
        type=str,
        help="Ziel-Keyword für die Content-Generierung"
    )
    
    parser.add_argument(
        "--type",
        type=str,
        default="blog",
        choices=["blog", "produktbeschreibung", "kategorie", "ratgeber", "vergleich"],
        help="Content-Typ (default: blog)"
    )
    
    parser.add_argument(
        "--target-score",
        type=int,
        default=75,
        help="Ziel Content Score (default: 75)"
    )
    
    parser.add_argument(
        "--word-count",
        type=int,
        help="Gewünschte Wortanzahl (optional)"
    )
    
    parser.add_argument(
        "--generate-images",
        type=int,
        default=3,
        help="Anzahl zu generierender Bilder (0 = keine, default: 3)"
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Interaktiver Modus mit Benutzerführung"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default="config.json",
        help="Pfad zur Konfigurationsdatei (default: config.json)"
    )
    
    args = parser.parse_args()
    
    # Interaktiver Modus
    if args.interactive:
        interactive_mode()
        return
    
    # Keyword erforderlich im nicht-interaktiven Modus
    if not args.keyword:
        parser.print_help()
        print("\n❌ Fehler: --keyword ist erforderlich (oder nutze --interactive)")
        sys.exit(1)
    
    # Generator starten
    try:
        generator = SEOContentGenerator(args.config)
        result = generator.generate_content(
            keyword=args.keyword,
            content_type=args.type,
            target_score=args.target_score,
            word_count=args.word_count,
            generate_images=args.generate_images > 0,
            image_count=args.generate_images
        )
        
        if result["success"]:
            print(f"\n✅ Erfolgreich! Score: {result['final_score']}/100")
            print(f"💾 Output: {result['output_path']}")
            sys.exit(0)
        else:
            print(f"\n❌ Fehler: {result.get('error', 'Unbekannter Fehler')}")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Fehler: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
