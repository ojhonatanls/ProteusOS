"""
ProteusOS - Sistema Operacional Minimalista e Modular
Version: 2.0.1
"""

__version__ = "2.0.1"
__author__ = "Jhonatan L. Santos"
__license__ = "MIT"
__description__ = "Sistema Operacional Minimalista e Modular com suporte a snapshots atômicos, rollback e gerenciamento de pacotes"

from .builder import SystemBuilder
from .pkg_manager import PackageManager
from .updater import SystemUpdater
from .config import Config
from .logger import setup_logging, get_logger
from .constants import *

VERSION = __version__
SYSTEM_NAME = "ProteusOS"
SYSTEM_DESCRIPTION = __description__
