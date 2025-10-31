"""
HTML Builder - Erstellt Bootstrap 4 HTML aus Content
"""

from typing import Dict, List
import markdown
from bs4 import BeautifulSoup
from datetime import datetime
from src.utils.logger import get_logger


class HTMLBuilder:
    """Baut HTML-Output mit Bootstrap 4"""
    
    def __init__(self, config):
        """
        Initialisiere HTML Builder
        
        Args:
            config: Config-Objekt
        """
        self.config = config
        self.logger = get_logger()
    
    def build(self, text: str, meta_data: Dict, images: List[Dict], keyword: str, content_type: str) -> str:
        """
        Baue vollständiges HTML-Dokument
        
        Args:
            text: Content-Text (Markdown)
            meta_data: Meta-Daten (title, description, h1)
            images: Bild-Daten
            keyword: Keyword
            content_type: Content-Typ
            
        Returns:
            Vollständiges HTML
        """
        self.logger.debug("Baue HTML-Output")
        
        # Konvertiere Markdown zu HTML
        content_html = self._markdown_to_html(text)
        
        # Integriere Bilder
        content_html = self._integrate_images(content_html, images)
        
        # Baue vollständiges HTML
        html = self._build_full_html(content_html, meta_data, keyword, content_type)
        
        self.logger.debug("✓ HTML-Output erstellt")
        
        return html
    
    def _markdown_to_html(self, text: str) -> str:
        """
        Konvertiere Markdown zu HTML
        
        Args:
            text: Markdown-Text
            
        Returns:
            HTML
        """
        # Konvertiere mit Python-Markdown
        html = markdown.markdown(
            text,
            extensions=['extra', 'nl2br', 'sane_lists']
        )
        
        # Parse und verbessere HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # Füge Bootstrap-Klassen hinzu
        soup = self._add_bootstrap_classes(soup)
        
        return str(soup)
    
    def _add_bootstrap_classes(self, soup: BeautifulSoup) -> BeautifulSoup:
        """
        Füge Bootstrap-Klassen zu HTML-Elementen hinzu
        
        Args:
            soup: BeautifulSoup-Objekt
            
        Returns:
            Modifiziertes BeautifulSoup-Objekt
        """
        # Tabellen
        for table in soup.find_all('table'):
            table['class'] = table.get('class', []) + ['table', 'table-striped', 'table-hover']
        
        # Bilder
        for img in soup.find_all('img'):
            img['class'] = img.get('class', []) + ['img-fluid', 'rounded', 'shadow-sm']
        
        # Blockquotes
        for blockquote in soup.find_all('blockquote'):
            blockquote['class'] = blockquote.get('class', []) + ['blockquote', 'border-left', 'pl-3']
        
        # Listen
        for ul in soup.find_all('ul'):
            ul['class'] = ul.get('class', []) + ['list-unstyled', 'ml-3']
        
        return soup
    
    def _integrate_images(self, html: str, images: List[Dict]) -> str:
        """
        Integriere Bilder in HTML
        
        Args:
            html: HTML-Content
            images: Bild-Daten
            
        Returns:
            HTML mit integrierten Bildern
        """
        if not images:
            return html
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Finde alle H2-Überschriften
        h2_tags = soup.find_all('h2')
        
        # Verteile Bilder nach H2-Überschriften
        for i, img_data in enumerate(images):
            if i < len(h2_tags):
                # Erstelle Bild-Element
                img_html = self._create_image_html(img_data)
                img_soup = BeautifulSoup(img_html, 'html.parser')
                
                # Füge nach H2 ein
                h2_tags[i].insert_after(img_soup)
        
        # Falls mehr Bilder als H2s: Füge am Ende hinzu
        if len(images) > len(h2_tags):
            for img_data in images[len(h2_tags):]:
                img_html = self._create_image_html(img_data)
                img_soup = BeautifulSoup(img_html, 'html.parser')
                soup.append(img_soup)
        
        return str(soup)
    
    def _create_image_html(self, img_data: Dict) -> str:
        """
        Erstelle HTML für Bild
        
        Args:
            img_data: Bild-Daten
            
        Returns:
            HTML-String
        """
        # Verwende relativen Pfad für Web
        img_path = f"/images/banner/{Path(img_data['path']).name}"
        
        html = f"""
<figure class="figure my-4">
    <img src="{img_path}" 
         class="figure-img img-fluid rounded shadow" 
         alt="{img_data['alt']}" 
         title="{img_data['title']}"
         loading="lazy">
    <figcaption class="figure-caption text-center">{img_data['alt']}</figcaption>
</figure>
"""
        return html
    
    def _build_full_html(self, content_html: str, meta_data: Dict, keyword: str, content_type: str) -> str:
        """
        Baue vollständiges HTML-Dokument
        
        Args:
            content_html: Content-HTML
            meta_data: Meta-Daten
            keyword: Keyword
            content_type: Content-Typ
            
        Returns:
            Vollständiges HTML
        """
        timestamp = datetime.now().strftime("%d.%m.%Y")
        
        html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    
    <!-- SEO Meta Tags -->
    <title>{meta_data['title']}</title>
    <meta name="description" content="{meta_data['description']}">
    <meta name="keywords" content="{keyword}">
    <meta name="author" content="SEO Content Generator">
    <meta name="robots" content="index, follow">
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="article">
    <meta property="og:title" content="{meta_data['title']}">
    <meta property="og:description" content="{meta_data['description']}">
    
    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:title" content="{meta_data['title']}">
    <meta property="twitter:description" content="{meta_data['description']}">
    
    <!-- Bootstrap 4 CSS -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css">
    
    <!-- Custom Styles -->
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.7;
            color: #333;
        }}
        
        .content-wrapper {{
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        
        h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            color: #1a1a1a;
        }}
        
        h2 {{
            font-size: 1.8rem;
            font-weight: 600;
            margin-top: 2.5rem;
            margin-bottom: 1rem;
            color: #2c3e50;
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 0.5rem;
        }}
        
        h3 {{
            font-size: 1.4rem;
            font-weight: 600;
            margin-top: 2rem;
            margin-bottom: 0.8rem;
            color: #34495e;
        }}
        
        p {{
            margin-bottom: 1.2rem;
            font-size: 1.05rem;
        }}
        
        strong {{
            font-weight: 600;
            color: #2c3e50;
        }}
        
        ul, ol {{
            margin-bottom: 1.5rem;
            padding-left: 2rem;
        }}
        
        li {{
            margin-bottom: 0.5rem;
        }}
        
        .figure {{
            margin: 2rem 0;
        }}
        
        .figure-img {{
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .meta-info {{
            color: #6c757d;
            font-size: 0.9rem;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .table {{
            margin: 2rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .blockquote {{
            border-left: 4px solid #007bff;
            background-color: #f8f9fa;
            padding: 1rem 1.5rem;
            margin: 1.5rem 0;
        }}
        
        @media (max-width: 768px) {{
            h1 {{
                font-size: 2rem;
            }}
            h2 {{
                font-size: 1.5rem;
            }}
            .content-wrapper {{
                padding: 20px 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="content-wrapper">
        <!-- Header -->
        <header>
            <h1>{meta_data['h1']}</h1>
            <div class="meta-info">
                <span>📅 Erstellt am {timestamp}</span> | 
                <span>📝 Content-Typ: {content_type}</span> |
                <span>🔑 Keyword: {keyword}</span>
            </div>
        </header>
        
        <!-- Main Content -->
        <article>
            {content_html}
        </article>
        
        <!-- Footer -->
        <footer class="mt-5 pt-4 border-top text-center text-muted">
            <p>Generiert mit SEO Content Generator | {timestamp}</p>
        </footer>
    </div>
    
    <!-- Bootstrap 4 JS -->
    <script src="https://cdn.jsdelivr.net/npm/jquery@3.5.1/dist/jquery.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""
        
        return html


from pathlib import Path
