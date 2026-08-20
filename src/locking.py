#!/usr/bin/env python3
"""
ProteusOS - Controle de Concorrência (File Locking)
"""

import fcntl
import os
from pathlib import Path
from contextlib import contextmanager

@contextmanager
def file_lock(lock_file: Path, timeout: int = 10):
    """
    Context manager para locking de arquivos.
    Garante que apenas um processo acesse o arquivo por vez.
    """
    lock_file = Path(lock_file)
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(lock_file, 'w') as f:
        try:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            yield
        except BlockingIOError:
            raise RuntimeError(f"Arquivo '{lock_file}' está bloqueado. Tente novamente mais tarde.")
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

@contextmanager
def shared_lock(lock_file: Path, timeout: int = 10):
    """
    Context manager para locking compartilhado (leitura).
    """
    lock_file = Path(lock_file)
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(lock_file, 'w') as f:
        try:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH | fcntl.LOCK_NB)
            yield
        except BlockingIOError:
            raise RuntimeError(f"Arquivo '{lock_file}' está bloqueado para leitura.")
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
