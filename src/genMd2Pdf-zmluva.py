import sys
import re
from pathlib import Path

try:
    import markdown
    from weasyprint import HTML
except ImportError:
    print("Chyba: Chýbajú potrebné knižnice.")
    print("Nainštaluj ich pomocou: pip install markdown weasyprint")
    sys.exit(1)

CSS_STYLES = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

@page {
    size: A4;
    margin: 20mm 20mm 20mm 20mm;
     
    @bottom-right {
        content: counter(page) " / " counter(pages);
        font-family: 'Inter', sans-serif;
        font-size: 9pt;
        color: #718096;
        font-weight: 400;
    }
}

*, *::before, *::after {
    box-sizing: border-box;
}

body {
    font-family: 'Inter', Arial, sans-serif;
    font-size: 10.5pt;
    line-height: 1.5;
    color: #2D3748;
    background-color: #FDFBFB;
    margin: 0;
    padding: 0;
}

h1 {
    font-size: 14pt;
    font-weight: 700;
    color: #2D3748;
    text-align: center;
    margin-top: 0px;
    margin-bottom: 25px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    line-height: 1.3;
    clear: both;
}

h2 {
    font-size: 11pt;
    font-weight: 700;
    color: #742A2A;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 22px;
    margin-bottom: 10px;
    text-align: left !important;
    page-break-after: avoid;
    border-bottom: 1px solid #FEB2B2;
    padding-bottom: 4px;
    clear: both;
}

h3 {
    font-size: 11pt;
    font-weight: 700;
    color: #742A2A;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 22px;
    margin-bottom: 10px;
    text-align: left !important;
    page-break-after: avoid;
    border-bottom: 1px solid #FEB2B2;
    padding-bottom: 4px;
    clear: both;
}

p {
    margin-top: 0;
    margin-bottom: 10px;
    text-align: justify;
    text-justify: inter-word;
}

/* Vlastné štýly pre farebné alert boxy so slovenskými labelmi */
.alert {
    padding: 12px 15px;
    margin: 15px 0;
    border-left: 4px solid;
    border-radius: 4px;
    font-size: 9.5pt;
    page-break-inside: avoid;
}

.alert p {
    margin: 0;
    text-align: left;
}

.alert-warning {
    background-color: #FFFAF0;
    border-color: #DD6B20;
    color: #7B341E;
}

.alert-note {
    background-color: #F0FFF4;
    border-color: #38A169;
    color: #22543D;
}

ul, ol {
    margin-top: 5px;
    margin-bottom: 10px;
    padding-left: 20px;
    text-align: left;
    clear: both;
}

li {
    margin-bottom: 4px;
    text-align: justify;
}
"""

def preprocess_markdown(text):
    text = text.replace('\xa0', ' ')
    text = text.replace('\u00a0', ' ')
    text = text.replace('m²', 'm&sup2;')
    text = text.replace('m^2', 'm&sup2;')
    
    # Bezpečne konvertuje bloky na čisté alert divy pre WeasyPrint
    text = re.sub(
        r'>\s*\[!CAUTION\]\s*\n>\s*(.*)', 
        r'<div class="alert alert-warning"><strong>⚠️ Upozornenie:</strong> \1</div>', 
        text
    )
    text = re.sub(
        r'>\s*\[!INFO\]\s*\n>\s*>\s*\n>\s*>\s*<span style="color: red;">(.*?)<\/span>', 
        r'<div class="alert alert-note"><strong>🟢 Poznámka:</strong> <span style="color: #22543D;">\1</span></div>', 
        text, 
        flags=re.DOTALL
    )
    
    return text

def convert_md_to_pdf(md_path_str, custom_title=None):
    md_path = Path(md_path_str)
    
    if not md_path.is_file():
        print(f"Chyba: Súbor '{md_path}' neexistuje.")
        sys.exit(1)
        
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
    except UnicodeDecodeError:
        with open(md_path, 'r', encoding='windows-1250') as f:
            md_content = f.read()
        
    document_title = custom_title if custom_title else md_path.stem
    cleaned_md = preprocess_markdown(md_content)

    html_body = markdown.markdown(cleaned_md, extensions=['tables', 'fenced_code', 'attr_list', 'sane_lists'])
    
    full_html = f"""
    <!DOCTYPE html>
    <html lang="sk">
    <head>
        <meta charset="utf-8">
        <title>{document_title}</title>
        <style>
            {CSS_STYLES}
        </style>
    </head>
    <body>
        <div>
            {html_body}
        </div>
    </body>
    </html>
    """
    
    pdf_dir = md_path.parent / "pdf"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = pdf_dir / f"{md_path.stem}.pdf"
        
    print(f"Generujem PDF: '{document_title}' -> {pdf_path.name}...")
    
    try:
        HTML(string=full_html, base_url=str(md_path.parent.resolve())).write_pdf(str(pdf_path))
        print(f"Úspešne dokončené! Súbor: {pdf_path.resolve()}")
    except Exception as e:
        print(f"Chyba pri generovaní PDF cez WeasyPrint: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Použitie: python genMd2Pdf.py <cesta_k_markdown_suboru> [volitelny_titulok]")
        sys.exit(1)
        
    md_file = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else None
    
    convert_md_to_pdf(md_file, title)