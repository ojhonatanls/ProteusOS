#!/usr/bin/env python3
"""
ProteusOS - Constantes Centralizadas
"""

from pathlib import Path

# Diretórios
SNAPSHOTS_DIR = "snapshots"
PACKAGES_DIR = "packages"
UPDATES_DIR = "updates"
EXPORTS_DIR = "proteus_exports"
TEMP_BUILD_DIR = "temp_build"

# Arquivos
METADATA_FILE = "metadata.json"
METADATA_BACKUP = "metadata.json.bak"
PACKAGE_METADATA = "package.json"
UPDATE_METADATA = "update_metadata.json"
CONFIG_FILE = ".proteusrc"

# Nomes de snapshot
SNAPSHOT_PREFIX = "snapshot"
PACKAGE_PREFIX = "pkg"
UPDATE_PREFIX = "update"

# Valores padrão
DEFAULT_BASE_DIR = Path.home() / "proteus_os"
DEFAULT_IMAGE = "alpine"
DEFAULT_KEEP_SNAPSHOTS = 5

# Constantes de tempo
DATE_FORMAT = "%Y%m%d_%H%M%S"
ISO_FORMAT = "%Y-%m-%dT%H:%M:%S"

# Segurança
MAX_FILENAME_LENGTH = 255
ALLOWED_FILENAME_CHARS = r'[^a-zA-Z0-9_.-]'
