#!/usr/bin/env python3
"""
ProteusOS - SystemUpdater
Gerencia atualizações atômicas e rollback.
"""

import os
import shutil
import tarfile
import tempfile
import json  # <-- LINHA ADICIONADA
from pathlib import Path
from typing import Dict
import datetime

from builder import SystemBuilder

class SystemUpdater:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.builder = SystemBuilder(base_dir)
        self.updates_dir = self.base_dir / "updates"
        self._ensure_directories()

    def _ensure_directories(self):
        """Cria os diretórios necessários."""
        self.updates_dir.mkdir(parents=True, exist_ok=True)

    def apply_update(self, update_path: str) -> str:
        """
        Aplica uma atualização de forma atômica.
        A atualização deve ser um .tar.gz com os novos arquivos.
        """
        update_path = Path(update_path)
        if not update_path.exists():
            raise FileNotFoundError(f"Atualização não encontrada: {update_path}")

        # Gera um ID para a atualização
        update_id = f"update_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        update_dir = self.updates_dir / update_id

        # Extrai a atualização em um diretório temporário
        temp_dir = Path(tempfile.mkdtemp(prefix="proteus_update_"))
        try:
            with tarfile.open(update_path, "r:gz") as tar:
                tar.extractall(temp_dir)

            # Verifica se há um script de atualização ou arquivos
            if not any(temp_dir.iterdir()):
                raise ValueError("Atualização vazia")

            # Move a atualização para o diretório de updates
            shutil.copytree(temp_dir, update_dir)

            # Cria um novo snapshot (simula a imagem atômica)
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

        return snapshot_id

    def rollback(self, snapshot_id: str = None) -> str:
        """
        Realiza rollback para um snapshot específico ou o último estável.
        """
        if snapshot_id is None:
            # Obtém todos os snapshots e escolhe o penúltimo (rollback do último)
            snapshots = self.builder.get_status()
            if len(snapshots) < 2:
                raise ValueError("Não há snapshots suficientes para rollback")
            snapshot_id = snapshots[-2]  # Penúltimo snapshot

        # Realiza o rollback via builder
        self.builder.rollback_to_snapshot(snapshot_id)
        return snapshot_id
