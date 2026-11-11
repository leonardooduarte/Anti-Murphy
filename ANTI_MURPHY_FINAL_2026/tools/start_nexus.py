"""V30.0.2 bootstrap. Standard-library only; never requires global Streamlit."""
from __future__ import annotations
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import venv
import socket
import threading
import time
import webbrowser

MIN_PYTHON = (3, 11)
REQUIRED_MODULES = ('streamlit', 'pandas', 'numpy', 'plotly', 'openpyxl')


class StartupError(Exception):
    pass


def supported(version):
    """Do not reject a newer interpreter solely because of an arbitrary upper bound."""
    return tuple(version[:2]) >= MIN_PYTHON


class Log:
    def __init__(self, path):
        self.path = Path(path)

    def write(self, message):
        text = str(message)
        print(text, flush=True)
        with self.path.open('a', encoding='utf-8', errors='replace') as f:
            f.write(text + '\n')


def interpreter_info(executable):
    code = "import json,sys; print(json.dumps({'version':list(sys.version_info[:3]),'executable':sys.executable}))"
    try:
        r = subprocess.run([str(executable), '-I', '-c', code], capture_output=True, text=True, timeout=20)
        if r.returncode:
            return None
        info = json.loads(r.stdout.strip())
        if not isinstance(info, dict) or not isinstance(info.get('version'), list):
            return None
        return info
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None


def environment_python(root, windows=None):
    if windows is None:
        windows = os.name == 'nt'
    return Path(root) / '.venv' / ('Scripts/python.exe' if windows else 'bin/python')


def create_environment(directory):
    venv.EnvBuilder(with_pip=True).create(str(directory))


def ensure_environment(root, log, *, windows=None):
    target = environment_python(root, windows)
    info = interpreter_info(target) if target.is_file() else None
    if info and supported(info['version']):
        log.write('[1/3] Reutilizando ambiente do projeto: ' + str(target))
        return target
    directory = Path(root) / '.venv'
    if directory.exists():
        stamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        backup = directory.with_name('.venv_anterior_' + stamp)
        try:
            directory.rename(backup)
        except OSError as exc:
            raise StartupError('O ambiente antigo nao pode ser movido. Feche os terminais que o utilizam. Detalhe: ' + str(exc)) from exc
        log.write('Ambiente anterior preservado em: ' + str(backup))
    log.write('[1/3] Criando ambiente isolado com Python ' + sys.version.split()[0] + '...')
    try:
        create_environment(directory)
    except (OSError, subprocess.SubprocessError) as exc:
        raise StartupError('Nao foi possivel criar .venv. Verifique permissoes e a instalacao completa do Python. Detalhe: ' + str(exc)) from exc
    info = interpreter_info(target)
    if not info or not supported(info['version']):
        raise StartupError('O ambiente .venv foi criado, mas seu Python nao iniciou corretamente.')
    return target


def dependencies_ready(executable):
    code = (
        "import sys,streamlit,pandas,numpy,plotly,openpyxl; "
        "from importlib.metadata import version; "
        "v=lambda name:tuple(map(int,version(name).split('.')[:3])); "
        "assert (1,66)<=v('streamlit')<(2,); "
        "assert ((3,0,6)==v('pandas') if sys.version_info[:2]>=(3,15) else (2,2)<=v('pandas')<(3,)); "
        "assert (1,26)<=v('numpy')<(3,); "
        "assert (5,22)<=v('plotly')<(8,); "
        "assert (3,1,5)<=v('openpyxl')<(4,)"
    )
    try:
        return subprocess.run([str(executable), '-I', '-c', code], capture_output=True, timeout=40).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def run_logged(argv, root, log):
    """Argument arrays preserve paths with spaces; no shell string interpolation."""
    try:
        p = subprocess.Popen([str(a) for a in argv], cwd=str(root), stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace',
                             env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
        assert p.stdout is not None
        for line in p.stdout:
            log.write(line.rstrip('\r\n'))
        return p.wait()
    except OSError as exc:
        raise StartupError('Nao foi possivel executar ' + str(argv[0]) + ': ' + str(exc)) from exc


def ensure_dependencies(executable, root, log):
    if dependencies_ready(executable):
        log.write('[2/3] Dependencias OK.')
        return
    log.write('[2/3] Instalando dependencias no ambiente do projeto...')
    pip = [str(executable), '-m', 'pip']
    if run_logged(pip + ['--version'], root, log):
        if run_logged([str(executable), '-m', 'ensurepip', '--upgrade'], root, log):
            raise StartupError('O pip nao ficou disponivel dentro de .venv.')
    if run_logged(pip + ['install', '--only-binary=:all:', '-r', str(Path(root) / 'requirements.txt')], root, log):
        raise StartupError('A instalacao de dependencias falhou. Foram permitidos apenas pacotes prontos, sem compilacao. A mensagem original do pip esta acima e no diagnostico.')
    if not dependencies_ready(executable):
        raise StartupError('A instalacao terminou, mas a verificacao de dependencias ainda falhou. Consulte o diagnostico.')


def available_port(start=8501, attempts=12):
    """Select an unused localhost port; do not silently connect to an older app."""
    for port in range(start, start + attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    raise StartupError('Não foi encontrada uma porta local livre entre 8501 e 8512.')


def launch_arguments(executable, root, port=8501):
    return [str(executable), '-m', 'streamlit', 'run', str(Path(root) / 'app.py'),
            '--server.port=' + str(port), '--server.headless=true',
            '--server.address=127.0.0.1']


def open_browser_when_ready(port, log, timeout_seconds=60):
    """Launch default browser only when THIS Streamlit server is listening."""
    url = 'http://127.0.0.1:' + str(port)
    for _ in range(int(timeout_seconds * 2)):
        try:
            with socket.create_connection(('127.0.0.1', port), timeout=0.4):
                pass
            if not webbrowser.open(url, new=2):
                log.write('Abra este endereço no navegador: ' + url)
            else:
                log.write('Navegador aberto: ' + url)
            return
        except OSError:
            time.sleep(0.5)
    log.write('A inicialização demorou. Se necessário, abra: ' + url)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    parser.add_argument('logfile', type=Path)
    parser.add_argument('--diagnose-only', action='store_true')
    args = parser.parse_args(argv)
    root = args.root.resolve()
    log = Log(args.logfile)
    try:
        log.write('Python selecionado: ' + sys.executable)
        log.write('Versao: ' + sys.version.replace('\n', ' '))
        if not supported(sys.version_info):
            raise StartupError('Este pacote requer Python 3.11 ou superior. O Python selecionado e mais antigo.')
        if not (root / 'app.py').is_file() or not (root / 'requirements.txt').is_file():
            raise StartupError('Arquivos do projeto ausentes. Extraia o ZIP completo antes de executar o inicializador.')
        if args.diagnose_only:
            log.write('Projeto e Python reconhecidos. Nenhum ambiente ou pacote foi alterado.')
            return 0
        executable = ensure_environment(root, log)
        ensure_dependencies(executable, root, log)
        port = available_port()
        log.write('[3/3] Iniciando Anti-Murphy (ferramentas completas) na porta ' + str(port) + '...')
        log.write('O navegador abrirá automaticamente. Para encerrar: CTRL+C.')
        threading.Thread(target=open_browser_when_ready, args=(port, log), daemon=True).start()
        result = run_logged(launch_arguments(executable, root, port=port), root, log)
        if result:
            raise StartupError('O Streamlit encerrou com codigo ' + str(result) + '. Veja a mensagem original acima.')
        return 0
    except KeyboardInterrupt:
        log.write('Aplicativo encerrado pelo usuario.')
        return 0
    except StartupError as exc:
        log.write('ERRO: ' + str(exc))
        return 1
    except Exception as exc:
        log.write('ERRO de inicializacao (' + type(exc).__name__ + '): ' + str(exc))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
