"""Best-effort multi-file local persistence with staged atomic replacements.

The rollback covers ordinary write/replace failures; like any file transaction
without a journaling filesystem it cannot guarantee recovery from power loss.
"""
from __future__ import annotations
import json
import os
import tempfile
from pathlib import Path


def atomic_bundle(files: dict[Path, object]) -> None:
    staged = {}
    originals = {}
    committed = []
    try:
        for target, payload in files.items():
            target = Path(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            encoded = json.dumps(payload, ensure_ascii=False, indent=2,
                                 allow_nan=False).encode('utf-8')
            originals[target] = target.read_bytes() if target.exists() else None
            with tempfile.NamedTemporaryFile(mode='wb', dir=target.parent,
                   prefix='.anti_murphy_', suffix='.tmp', delete=False) as f:
                staged[target] = Path(f.name)
                f.write(encoded)
                f.flush()
                os.fsync(f.fileno())
        for target, temp in staged.items():
            os.replace(temp, target)
            committed.append(target)
    except Exception:
        for target in reversed(committed):
            previous = originals[target]
            try:
                if previous is None:
                    target.unlink(missing_ok=True)
                else:
                    with tempfile.NamedTemporaryFile(mode='wb', dir=target.parent,
                            prefix='.restore_', suffix='.tmp', delete=False) as f:
                        undo = Path(f.name)
                        f.write(previous)
                        f.flush()
                        os.fsync(f.fileno())
                    os.replace(undo, target)
            except OSError:
                # Checkpoint remains independent; callers must report the error.
                pass
        raise
    finally:
        for temp in staged.values():
            temp.unlink(missing_ok=True)
