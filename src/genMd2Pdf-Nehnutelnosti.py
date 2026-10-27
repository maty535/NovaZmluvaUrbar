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

h2, h3, h4 {
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
}

p {
    margin-top: 0;
    margin-bottom: 10px;
    text-align: justify;
    text-justify: inter-word;
}

hr {
    border: 0;
    border-top: 0.5px solid #FEB2B2;
    margin: 20px 0;
    clear: both;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
    margin-bottom: 15px;
    font-size: 9.5pt;
    page-break-inside: avoid;
}

th, td {
    border: 1px solid #FEB2B2;
    padding: 6px 10px;
    text-align: left;
}

th {
    background-color: #FFF5F5;
    color: #742A2A;
    font-weight: 600;
    text-transform: uppercase;
    font-size: 8.5pt;
    letter-spacing: 0.3px;
}

tr:nth-child(even) {
    background-color: #FFF9F9;
}
"""

def preprocess_markdown(text):
    text = text.replace('\xa0', ' ')
    text = text.replace('\u00a0', ' ')
    text = text.replace('m²', 'm&sup2;')
    text = text.replace('m^2', 'm&sup2;')
    
    # Automaticky zabezpečí prázdny riadok pred tabuľkou, ak tam náhodou chýba
    text = re.sub(r'(\*\*LV č\.[^*]+\*\*)\n(\|)', r'\1\n\n\2', text)
    
    text = re.sub(r'[ \t]+\|', '|', text)
    text = re.sub(r'\|[ \t]+', '|', text)
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

    html_body = markdown.markdown(cleaned_md, extensions=['tables', 'fenced_code', 'attr_list'])
    
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
    
    pdf_path = md_path.with_suffix('.pdf')
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