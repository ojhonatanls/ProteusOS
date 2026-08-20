#!/usr/bin/env python3
"""
ProteusOS - SystemUpdater
Gerencia atualizações atômicas e rollback.
"""

import os
import shutil
import tarfile
import tempfile
import json
import re
from pathlib import Path
from typing import Dict, Optional
import datetime

from constants import UPDATES_DIR, UPDATE_PREFIX, ALLOWED_FILENAME_CHARS
from logger import get_logger
from locking import file_lock
from builder import SystemBuilder

logger = get_logger()

class SystemUpdater:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.builder = SystemBuilder(base_dir)
        self.updates_dir = self.base_dir / UPDATES_DIR
        self.lock_file = self.base_dir / "updates.lock"
        self._ensure_directories()

    def _ensure_directories(self):
        """Cria os diretórios necessários."""
        self.updates_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_filename(self, name: str) -> str:
        """Sanitiza um nome para uso em nomes de arquivos."""
        if not name:
            return "unknown"
        sanitized = re.sub(ALLOWED_FILENAME_CHARS, '_', name)
        return sanitized[:255]

    def apply_update(self, update_path: str) -> str:
        """
        Aplica uma atualização de forma atômica.
        A atualização deve ser um .tar.gz com os novos arquivos.
        """
        update_path = Path(update_path)
        if not update_path.exists():
            raise FileNotFoundError(f"Atualização não encontrada: {update_path}")

        logger.info(f"Aplicando atualização: {update_path}")

        # Gera um ID para a atualização
        update_id = f"{UPDATE_PREFIX}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        update_dir = self.updates_dir / update_id

        # Extrai a atualização em um diretório temporário
        temp_dir = Path(tempfile.mkdtemp(prefix="proteus_update_"))
        try:
            with tarfile.open(update_path, "r:gz") as tar:
                tar.extractall(temp_dir)

            if not any(temp_dir.iterdir()):
                raise ValueError("Atualização vazia")

            # Move a atualização para o diretório de updates
            shutil.copytree(temp_dir, update_dir)

            # Cria um novo snapshot
            snapshot_id = self.builder.build_base("updated")

            # Adiciona metadados da atualização
            metadata = {
                "update_id": update_id,
                "snapshot_id": snapshot_id,
                "timestamp": datetime.datetime.now().isoformat()
            }
            (update_dir / "update_metadata.json").write_text(
                json.dumps(metadata, indent=2)
            )

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        logger.info(f"Atualização aplicada: {snapshot_id}")
        return snapshot_id

    def rollback(self, snapshot_id: Optional[str] = None) -> str:
        """
        Realiza rollback para um snapshot específico ou o último estável.
        """
        if snapshot_id is None:
            snapshots = self.builder.get_status()
            if len(snapshots) < 2:
                raise ValueError("Não há snapshots suficientes para rollback")
            snapshot_id = snapshots[-2]
            logger.info(f"Rollback para o penúltimo snapshot: {snapshot_id}")

        # Verifica integridade do snapshot
        if not self.builder.snapshot_exists(snapshot_id):
            raise FileNotFoundError(f"Snapshot '{snapshot_id}' não encontrado fisicamente")

        self.builder.rollback_to_snapshot(snapshot_id)
        logger.info(f"Rollback concluído para: {snapshot_id}")
        return snapshot_id
