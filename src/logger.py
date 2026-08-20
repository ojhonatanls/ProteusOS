#!/usr/bin/env python3
"""
ProteusOS - Sistema de Logging Centralizado
"""

import logging
import sys
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

def setup_logging(log_dir: Path = None, level: int = logging.INFO):
    """Configura o sistema de logging."""
    global _logger
    
    if _logger is not None:
        return _logger
    
    # Cria o logger
    logger = logging.getLogger('proteusos')
    logger.setLevel(level)
    
    # Remove handlers existentes
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    logger.addHandler(console_handler)
    
    # Handler para arquivo (se log_dir for fornecido)
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

# Funções de conveniência
def debug(msg, *args, **kwargs):
    get_logger().debug(msg, *args, **kwargs)

def info(msg, *args, **kwargs):
    get_logger().info(msg, *args, **kwargs)

def warning(msg, *args, **kwargs):
    get_logger().warning(msg, *args, **kwargs)

def error(msg, *args, **kwargs):
    get_logger().error(msg, *args, **kwargs)

def critical(msg, *args, **kwargs):
    get_logger().critical(msg, *args, **kwargs)
