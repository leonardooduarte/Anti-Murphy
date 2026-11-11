"""AM12: local OS advisory lock plus byte-level project revision.

Lock ownership is released by the OS on exit/crash; the lock file is never
removed (removal could split the lock between two independent file handles).
Only cooperating local processes are serialized, not network filesystems.
"""
from contextlib import contextmanager
from pathlib import Path
from threading import RLock, local
import hashlib
import os
import time

_registry = {}
_registry_lock = RLock()
_owned = local()


@contextmanager
def workspace_lock(storage, timeout=5.0):
    folder = Path(storage).resolve()
    folder.mkdir(parents=True, exist_ok=True)
    key = str(folder)
    with _registry_lock:
        gate = _registry.setdefault(key, RLock())
    if not gate.acquire(timeout=timeout):
        raise OSError('Projeto ocupado por outra gravação. Tente novamente.')
    depths = getattr(_owned, 'depths', None)
    if depths is None:
        depths = _owned.depths = {}
    handle = None
    locked = False
    try:
        if not depths.get(key):
            handle = (folder / '.workspace.lock').open('a+b')
            if os.name == 'nt' and os.fstat(handle.fileno()).st_size == 0:
                handle.write(b'\0');handle.flush()
            deadline = time.monotonic() + timeout
            while True:
                try:
                    if os.name == 'nt':
                        import msvcrt
                        handle.seek(0);msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                    else:
                        import fcntl
                        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    locked = True
                    break
                except OSError:
                    if time.monotonic() >= deadline:
                        raise OSError('Projeto ocupado por outra gravação. Tente novamente.')
                    time.sleep(.05)
        depths[key] = depths.get(key, 0) + 1
        try:
            yield
        finally:
            depths[key] -= 1
    finally:
        if handle:
            try:
                if locked:
                    if os.name == 'nt':
                        import msvcrt
                        handle.seek(0);msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                    else:
                        import fcntl
                        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            finally:
                handle.close()
        gate.release()


def project_revision(storage):
    """Project files only; appending decisions/experiments is not a model edit."""
    folder = Path(storage)
    paths = [folder/n for n in ('projeto.json','projeto_ativo.json','projeto_confirmado.json')]
    paths += sorted((folder/'projetos').glob('*.json'))
    digest = hashlib.sha256()
    for path in paths:
        name = str(path.relative_to(folder)).replace('\\','/').encode('utf8')
        content = path.read_bytes() if path.exists() else None
        digest.update(len(name).to_bytes(8,'big'));digest.update(name)
        digest.update(b'missing' if content is None else hashlib.sha256(content).digest())
    return digest.hexdigest()
