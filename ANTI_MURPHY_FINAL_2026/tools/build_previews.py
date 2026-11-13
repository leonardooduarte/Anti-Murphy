"""Build historical offline previews from the distributed template and fixture.

These are static examples, not the live Studio or the user's current project.
No simulation, network or workspace write is performed.
"""
import base64
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def preview_html(root=ROOT):
    bundle=json.loads((root/'factory_command_demo.json').read_text('utf-8'))
    raw=json.dumps(bundle,ensure_ascii=False,separators=(',',':'))
    raw=raw.replace('<',r'\u003c').replace('>',r'\u003e').replace('&',r'\u0026')
    brand='data:image/svg+xml;base64,'+base64.b64encode((root/'assets/brand/logo-light.svg').read_bytes()).decode()
    return (root/'ui/factory_studio.html').read_text('utf-8').replace('__BUNDLE_JSON__',raw).replace('__BRAND__',brand)


def build(root=ROOT):
    html=preview_html(root)
    for name in ('PREVIEW_OPERACAO.html','PREVIEW_FACTORY_COMMAND.html'):
        (root/name).write_text(html,encoding='utf-8')


if __name__=='__main__':
    build()
