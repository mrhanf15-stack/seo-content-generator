"""
Report Generator - Erstellt Reports und Dashboards
"""

from typing import Dict, List
from datetime import datetime
from src.utils.logger import get_logger


class ReportGenerator:
    """Generiert Reports und Analytics"""
    
    def __init__(self, config):
        """
        Initialisiere Report Generator
        
        Args:
            config: Config-Objekt
        """
        self.config = config
        self.logger = get_logger()
    
    def generate(
        self,
        keyword: str,
        final_text: str,
        score_result: Dict,
        competitor_data: Dict,
        meta_data: Dict,
        images: List[Dict],
        iterations: int
    ) -> Dict:
        """
        Generiere vollständigen Report
        
        Args:
            keyword: Keyword
            final_text: Finaler Text
            score_result: Scoring-Ergebnis
            competitor_data: Konkurrenz-Daten
            meta_data: Meta-Daten
            images: Generierte Bilder
            iterations: Anzahl Optimierungs-Iterationen
            
        Returns:
            Report-Daten
        """
        self.logger.debug("Generiere Report")
        
        timestamp = datetime.now().isoformat()
        
        report = {
            'metadata': {
                'keyword': keyword,
                'generated_at': timestamp,
                'iterations': iterations,
                'final_score': score_result['total_score'],
                'grade': score_result['grade']
            },
            'content_metrics': {
                'word_count': len(final_text.split()),
                'character_count': len(final_text),
                'images_generated': len(images)
            },
            'seo_meta': meta_data,
            'score_breakdown': {
                'total_score': score_result['total_score'],
                'keyword_optimization': {
                    'score': score_result['keyword_optimization']['score'],
                    'percentage': score_result['keyword_optimization']['percentage'],
                    'details': score_result['keyword_optimization']['details']
                },
                'structure_readability': {
                    'score': score_result['structure_readability']['score'],
                    'percentage': score_result['structure_readability']['percentage'],
                    'details': score_result['structure_readability']['details']
                },
                'content_quality': {
                    'score': score_result['content_quality']['score'],
                    'percentage': score_result['content_quality']['percentage'],
                    'details': score_result['content_quality']['details']
                },
                'technical_seo': {
                    'score': score_result['technical_seo']['score'],
                    'percentage': score_result['technical_seo']['percentage'],
                    'details': score_result['technical_seo']['details']
                },
                'engagement': {
                    'score': score_result['engagement']['score'],
                    'percentage': score_result['engagement']['percentage'],
                    'details': score_result['engagement']['details']
                }
            },
            'competitor_analysis': {
                'competitors_analyzed': competitor_data.get('competitor_count', 0),
                'benchmarks': competitor_data.get('benchmarks', {}),
                'insights': competitor_data.get('insights', {}),
                'top_competitors': [
                    {
                        'position': c.get('position', 0),
                        'url': c.get('url', ''),
                        'title': c.get('title', ''),
                        'word_count': c.get('word_count', 0),
                        'structure_score': c.get('structure_score', 0)
                    }
                    for c in competitor_data.get('competitors', [])[:5]
                ]
            },
            'images': [
                {
                    'number': img['number'],
                    'path': img['path'],
                    'alt': img['alt'],
                    'title': img['title']
                }
                for img in images
            ],
            'optimization_history': {
                'iterations': iterations,
                'improvements': self._calculate_improvements(score_result)
            },
            'recommendations': self._generate_recommendations(score_result, competitor_data)
        }
        
        self.logger.debug("✓ Report generiert")
        
        return report
    
    def _calculate_improvements(self, score_result: Dict) -> List[str]:
        """
        Berechne Verbesserungen
        
        Args:
            score_result: Scoring-Ergebnis
            
        Returns:
            Liste von Verbesserungen
        """
        improvements = []
        
        for category in ['keyword_optimization', 'structure_readability', 'content_quality', 'technical_seo', 'engagement']:
            cat_data = score_result.get(category, {})
            percentage = cat_data.get('percentage', 0)
            
            if percentage >= 80:
                improvements.append(f"✓ {category.replace('_', ' ').title()}: Exzellent ({percentage:.1f}%)")
            elif percentage >= 70:
                improvements.append(f"✓ {category.replace('_', ' ').title()}: Gut ({percentage:.1f}%)")
            else:
                improvements.append(f"⚠ {category.replace('_', ' ').title()}: Verbesserungspotential ({percentage:.1f}%)")
        
        return improvements
    
    def _generate_recommendations(self, score_result: Dict, competitor_data: Dict) -> List[str]:
        """
        Generiere Empfehlungen
        
        Args:
            score_result: Scoring-Ergebnis
            competitor_data: Konkurrenz-Daten
            
        Returns:
            Liste von Empfehlungen
        """
        recommendations = []
        
        total_score = score_result['total_score']
        
        if total_score >= 90:
            recommendations.append("🎉 Exzellenter Content! Bereit für Veröffentlichung.")
        elif total_score >= 75:
            recommendations.append("✅ Guter Content! Kleinere Optimierungen möglich.")
        else:
            recommendations.append("⚠ Content benötigt weitere Optimierung.")
        
        # Kategorie-spezifische Empfehlungen
        for category in ['keyword_optimization', 'structure_readability', 'content_quality', 'technical_seo', 'engagement']:
            cat_data = score_result.get(category, {})
            percentage = cat_data.get('percentage', 0)
            
            if percentage < 70:
                recommendations.append(f"🔧 Fokus auf {category.replace('_', ' ').title()}")
        
        # Konkurrenz-Vergleich
        benchmarks = competitor_data.get('benchmarks', {})
        avg_word_count = benchmarks.get('word_count', {}).get('avg', 0)
        
        if avg_word_count > 0:
            recommendations.append(f"📊 Durchschnittliche Konkurrenz-Länge: {int(avg_word_count)} Wörter")
        
        return recommendations
