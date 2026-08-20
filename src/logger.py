#!/usr/bin/env python3
"""
ProteusOS - Sistema de Logging Centralizado
"""

import logging
import sys
import re
from pathlib import Path
from datetime import datetime

# Configuração padrão
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Níveis de log
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

# Logger global
_logger = None

def sanitize_log_message(msg: str) -> str:
    """Sanitiza mensagens de log para remover informações sensíveis."""
    # Remove caminhos de arquivos sensíveis
    msg = re.sub(r'/home/[^/]+/', '/home/USER/', msg)
    msg = re.sub(r'/root/', '/root/', msg)
    # Remove tokens e chaves de API
    msg = re.sub(r'[a-zA-Z0-9]{32,}', '[REDACTED]', msg)
    return msg

def setup_logging(log_dir: Path = None, level: int = logging.INFO):
    """Configura o sistema de logging."""
    global _logger
    
    if _logger is not None:
        return _logger
    
    logger = logging.getLogger('proteusos')
    logger.setLevel(level)
    
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    logger.addHandler(console_handler)
    
    if log_dir:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"proteusos_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
        logger.addHandler(file_handler)
    
    _logger = logger
    return logger

def get_logger():
    """Retorna o logger configurado."""
    if _logger is None:
        return setup_logging()
    return _logger

# Funções de conveniência com sanitização
def debug(msg, *args, **kwargs):
    get_logger().debug(sanitize_log_message(msg), *args, **kwargs)

def info(msg, *args, **kwargs):
    get_logger().info(sanitize_log_message(msg), *args, **kwargs)

def warning(msg, *args, **kwargs):
    get_logger().warning(sanitize_log_message(msg), *args, **kwargs)

def error(msg, *args, **kwargs):
    get_logger().error(sanitize_log_message(msg), *args, **kwargs)

def critical(msg, *args, **kwargs):
    get_logger().critical(sanitize_log_message(msg), *args, **kwargs)
