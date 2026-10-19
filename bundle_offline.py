import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parent

with (ROOT / 'index.html').open('r', encoding='utf-8') as f:
    html = f.read()

with (ROOT / 'tailwind.min.css').open('r', encoding='utf-8') as f:
    tw_css = f.read()

with (ROOT / 'html2pdf.bundle.min.js').open('r', encoding='utf-8') as f:
    pdf_js = f.read()

# Replace Tailwind stylesheet link with inlined style
target_css_link = '<link rel="stylesheet" href="./tailwind.min.css" />'
inline_css = "<style>\n" + tw_css + "\n</style>"

if target_css_link in html:
    html = html.replace(target_css_link, inline_css)

# Replace html2pdf script tag with inlined script
target_pdf = """  <!-- html2pdf (Offline local with CDN fallback) -->
  <script src="./html2pdf.bundle.min.js"></script>
  <script>
    if (typeof html2pdf === 'undefined') {
      document.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"><\\/script>');
    }
  </script>"""

inline_pdf = "<script>\n" + pdf_js + "\n</script>"

if target_pdf in html:
    html = html.replace(target_pdf, inline_pdf)
else:
    html = html.replace('<script src="./html2pdf.bundle.min.js"></script>', inline_pdf)

# The legacy PDF ledger references this image directly (the app icons are embedded).
icon = base64.b64encode((ROOT / 'icon.jpg').read_bytes()).decode('ascii')
html = html.replace('src="./icon.jpg"', f'src="data:image/jpeg;base64,{icon}"')

with (ROOT / 'gameon.html').open('w', encoding='utf-8') as f:
    f.write(html)

print("Created 100% self-contained gameon.html. Total size:", len(html))
