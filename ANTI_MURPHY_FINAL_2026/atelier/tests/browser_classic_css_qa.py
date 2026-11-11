"""Static CSS sanity check. This does NOT execute historical Streamlit widgets."""
from pathlib import Path
import re
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
src=(ROOT/'ui/v29.py').read_text('utf8')
match=re.search(r"st\.markdown\('''(<style>[\s\S]*?</style>)''',unsafe_allow_html=True\)",src)
assert match,'ATLAS CSS not found'
styles=[match.group(1).replace('<style>','').replace('</style>',''),(ROOT/'ui/unified_shell.css').read_text('utf8'),(ROOT/'ui/classic_readability.css').read_text('utf8')]
markup='''<div class="stApp"><div data-testid="stAppViewContainer"><div data-testid="stMainBlockContainer">
<div data-testid="stMarkdownContainer" class="stMarkdown"><p id="plain">Observação operacional de alto contraste</p><h2 id="head">Análise técnica</h2></div>
<div data-testid="stCaptionContainer"><p id="caption">Origem do ensaio</p></div>
<div data-testid="stWidgetLabel"><p id="widget">Posto afetado</p></div>
<div class="am16-pagehead"><h1 id="pagehead">Visão 360</h1><p class="copy" id="pagecopy">Avalie a produção</p></div>
<div class="atlas-hero"><p id="hero">Texto dentro de painel escuro</p></div>
</div></div></div>'''
def rgb(css):
    if css.startswith('#'):
        css=css.lstrip('#');return [int(css[i:i+2],16) for i in (0,2,4)]
    nums=re.findall(r'[\d.]+',css)[:3]
    return [int(float(v)) for v in nums]
def luminance(rgb3):
    linear=[n/255/12.92 if n/255<=.04045 else ((n/255+.055)/1.055)**2.4 for n in rgb3]
    return sum(a*b for a,b in zip(linear,[.2126,.7152,.0722]))
def contrast(fg,bg):
    a,b=sorted([luminance(rgb(fg)),luminance(rgb(bg))],reverse=True)
    return (a+.05)/(b+.05)
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page()
    page.set_content(markup)
    for style in styles:page.add_style_tag(content=style)
    for selector,bg in [('plain','#F7F7F3'),('head','#F7F7F3'),('caption','#F7F7F3'),('widget','#F7F7F3'),('pagehead','#F7F7F3'),('pagecopy','#F7F7F3'),('hero','#17252A')]:
        col=page.locator('#'+selector).evaluate('(x)=>getComputedStyle(x).color')
        ratio=contrast(col,bg)
        print(selector,col,round(ratio,2))
        assert ratio>=4.5,selector
    browser.close()
