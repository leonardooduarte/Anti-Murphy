"""Local HTTP distribution smoke for 2026 premium presentation assets."""
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from urllib.request import urlopen
from http.server import ThreadingHTTPServer
import json
from atelier.service import Studio
from atelier import server


def check():
    with TemporaryDirectory() as tmp:
        server.STUDIO=Studio(Path(tmp))
        httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
        thread=Thread(target=httpd.serve_forever,daemon=True)
        thread.start()
        base=f'http://127.0.0.1:{httpd.server_port}'
        try:
            checks={
                '/':b'apresentacao_premium.css',
                '/app.js':b'presentationCompareViewBox',
                '/apresentacao_premium.css':b'presentation-compare-insights',
                '/api/state':b'decision_review',
                '/engineering_charts.js':b'AMCharts',
                '/final_banca.css':b'presentation-guide',
            }
            for path,expected in checks.items():
                with urlopen(base+path,timeout=10) as response:
                    raw=response.read()
                    assert response.status==200,(path,response.status)
                    assert expected in raw,(path,expected)
            with urlopen(base+'/api/state',timeout=10) as response:
                state=json.load(response)
            assert state['metrics']['normal']['sla_pct']>=0
            assert state['replay']['incident']['stations']
            print('HTTP Modo Banca Premium: HTML, CSS, JavaScript, métricas e replay OK',flush=True)
        finally:
            httpd.shutdown();httpd.server_close();thread.join(timeout=5)

if __name__=='__main__':check()
