"""Start a temporary local app, run optional Playwright QA, then stop it."""
from pathlib import Path
import os, socket, subprocess, sys, tempfile, time, urllib.request
root=Path(__file__).resolve().parents[1]
with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
with tempfile.TemporaryDirectory(prefix='anti-murphy-qa-records-') as record_dir, tempfile.TemporaryFile(mode='w+') as log:
    p=subprocess.Popen([sys.executable,'-m','streamlit','run',str(root/os.environ.get('AM_QA_APP','app.py')),'--server.headless=true','--server.address=127.0.0.1',f'--server.port={port}'],cwd=root,stdout=log,stderr=log,env={**os.environ,'AM_RECORD_DIR':record_dir})
    try:
        for _ in range(100):
            if p.poll() is not None:
                log.seek(0);raise RuntimeError(log.read())
            try:
                urllib.request.urlopen(f'http://127.0.0.1:{port}/_stcore/health',timeout=1).read();break
            except OSError:time.sleep(.2)
        env={**os.environ,'AM_QA_URL':f'http://127.0.0.1:{port}'}
        print('QA_URL',env['AM_QA_URL'],flush=True)
        r=subprocess.run(['node',str(root/os.environ.get('AM_QA_SCRIPT','tools/browser_qa.js'))],env=env,cwd=root,capture_output=True,text=True)
        sys.stdout.write(r.stdout);sys.stderr.write(r.stderr)
        if r.returncode==0 and 'BROWSER_QA_PASS' not in r.stdout:
            raise RuntimeError('Browser QA ended without a completion marker.')
        sys.exit(r.returncode)
    finally:
        p.terminate()
        try:p.wait(timeout=10)
        except subprocess.TimeoutExpired:p.kill()
