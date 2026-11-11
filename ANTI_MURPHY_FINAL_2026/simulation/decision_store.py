"""Local, atomic decision archives. Archived evidence never changes the live model."""
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import tempfile


def decode_record(raw):
    if len(raw)>10*1024*1024:raise ValueError('Registro maior que o limite de leitura.')
    body=json.loads(raw)
    if not isinstance(body,dict):raise ValueError('Registro inválido.')
    signed=dict(body);digest=signed.pop('sha256',None)
    if digest!=sha256(json.dumps(signed,sort_keys=True,ensure_ascii=False).encode()).hexdigest():
        raise ValueError('A integridade do registro não confere.')
    record=body.get('record') or {};examined=body.get('examined_action') or {}
    if not record or record.get('signature')!=examined.get('signature') or record.get('run_id')!=body.get('run_id'):
        raise ValueError('O arquivo precisa conter a decisão que foi registrada.')
    return body


def save_record(directory,raw):
    body=decode_record(raw);root=Path(directory);root.mkdir(parents=True,exist_ok=True)
    filename='decisao_'+body['sha256'][:24]+'.json';target=root/filename;temporary=None
    try:
        with tempfile.NamedTemporaryFile(mode='wb',prefix='.gravando_',suffix='.tmp',dir=root,delete=False) as f:
            temporary=Path(f.name);f.write(raw);f.flush();os.fsync(f.fileno())
        os.replace(temporary,target)
    finally:
        if temporary and temporary.exists():temporary.unlink()
    return target


def archived_records(directory):
    root=Path(directory);found=[]
    if not root.is_dir():return found
    for path in sorted(root.glob('decisao_*.json'),key=lambda p:p.stat().st_mtime,reverse=True)[:500]:
        if not re.fullmatch(r'decisao_[a-f0-9]{24}\.json',path.name):continue
        try:
            if path.stat().st_size>10*1024*1024:continue
            raw=path.read_bytes();body=decode_record(raw)
            found.append({'filename':path.name,'raw':raw,'data':body})
        except (OSError,ValueError,TypeError,KeyError):continue
    return found
