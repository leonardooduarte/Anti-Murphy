"""Distribuição HTTP: novo CSS/JS e resultados reais do motor no ZIP completo."""
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from urllib.request import urlopen
from http.server import ThreadingHTTPServer
from atelier.service import Studio
from atelier import server


def check():
    with TemporaryDirectory() as tmp:
        server.STUDIO = Studio(Path(tmp))
        httpd = ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        worker = Thread(target=httpd.serve_forever, daemon=True)
        worker.start()
        base = f'http://127.0.0.1:{httpd.server_port}'
        try:
            for path, expected in {
                '/': b'acabamento_banca_final.css',
                '/acabamento_banca_final.css': b'eng-index-legend',
                '/engineering_charts.js': b'indexedLegend',
                '/app.js': b'presentationEvidence',
                '/api/state': b'decision_review',
            }.items():
                with urlopen(base + path, timeout=15) as response:
                    content = response.read()
                    assert response.status == 200, (path, response.status)
                    assert expected in content, (path, expected)
            print('Distribuição HTTP do acabamento final: 5 rotas OK', flush=True)
        finally:
            httpd.shutdown()
            httpd.server_close()
            worker.join(timeout=5)

if __name__ == '__main__':
    check()
