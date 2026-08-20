#!/usr/bin/env python3
"""
ProteusOS - SystemBuilder
Gerencia a criação e versionamento de snapshots (imagens atômicas).
"""

import os
import shutil
import tarfile
import datetime
import json
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Optional

from constants import (
    SNAPSHOTS_DIR, METADATA_FILE, METADATA_BACKUP,
    SNAPSHOT_PREFIX, DATE_FORMAT, ISO_FORMAT,
    ALLOWED_FILENAME_CHARS, MAX_FILENAME_LENGTH
)
from logger import get_logger
from locking import file_lock

logger = get_logger()

class SystemBuilder:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.snapshots_dir = self.base_dir / SNAPSHOTS_DIR
        self.metadata_file = self.base_dir / METADATA_FILE
        self.lock_file = self.base_dir / "builder.lock"
        self._ensure_directories()

    def _ensure_directories(self):
        """Cria os diretórios necessários."""
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Diretórios criados em: {self.base_dir}")

    def _load_metadata(self) -> Dict:
        """Carrega os metadados dos snapshots com locking e recovery."""
        with file_lock(self.lock_file):
            if self.metadata_file.exists():
                try:
                    with open(self.metadata_file, 'r') as f:
                        return json.load(f)
                except json.JSONDecodeError as e:
                    logger.warning(f"Arquivo de metadados corrompido: {e}")
                    backup_file = self.metadata_file.with_suffix('.json.bak')
                    if backup_file.exists():
                        logger.info("Recuperando metadados do backup...")
                        with open(backup_file, 'r') as f:
                            return json.load(f)
                    logger.error("Não foi possível recuperar metadados. Criando novo.")
                    return {"snapshots": [], "current": None}
            return {"snapshots": [], "current": None}

    def _save_metadata(self, metadata: Dict):
        """Salva os metadados com backup automático e locking."""
        with file_lock(self.lock_file):
            if self.metadata_file.exists():
                shutil.copy2(self.metadata_file, self.metadata_file.with_suffix('.json.bak'))
                logger.debug("Backup dos metadados criado")
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            logger.debug("Metadados salvos com sucesso")

    def _sanitize_filename(self, name: str) -> str:
        """Sanitiza um nome para uso em nomes de arquivos."""
        if not name:
            return "unknown"
        sanitized = re.sub(ALLOWED_FILENAME_CHARS, '_', name)
        if len(sanitized) > MAX_FILENAME_LENGTH:
            sanitized = sanitized[:MAX_FILENAME_LENGTH]
        return sanitized

    def _generate_snapshot_id(self, base_image: str) -> str:
        """Gera um ID único para o snapshot."""
        timestamp = datetime.datetime.now().strftime(DATE_FORMAT)
        safe_image = self._sanitize_filename(base_image)
        return f"{SNAPSHOT_PREFIX}_{timestamp}_{safe_image}"

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calcula o checksum SHA-256 de um arquivo."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def snapshot_exists(self, snapshot_id: str) -> bool:
        """Verifica se um snapshot existe."""
        safe_id = self._sanitize_filename(snapshot_id)
        snapshot_path = self.snapshots_dir / f"{safe_id}.tar.gz"
        return snapshot_path.exists()

    def build_base(self, base_image: str) -> str:
        """
        Constrói um sistema base a partir de uma imagem.
        Na prática, cria um snapshot com uma estrutura de diretórios simulada.
        """
        logger.info(f"Iniciando build da imagem base: {base_image}")
        
        safe_image = self._sanitize_filename(base_image)
        snapshot_id = self._generate_snapshot_id(safe_image)
        snapshot_path = self.snapshots_dir / f"{snapshot_id}.tar.gz"

        print(f"   Construindo imagem base '{safe_image}'...")
        
        with tarfile.open(snapshot_path, "w:gz") as tar:
            temp_dir = self.base_dir / "temp_build"
            temp_dir.mkdir(exist_ok=True)

            (temp_dir / "etc").mkdir(exist_ok=True)
            (temp_dir / "etc" / "os-release").write_text(f"ID=proteus\nVERSION={safe_image}\n")
            (temp_dir / "bin").mkdir(exist_ok=True)
            (temp_dir / "bin" / "sh").write_text("#!/bin/sh\necho 'ProteusOS Shell'", encoding='utf-8')
            (temp_dir / "bin" / "sh").chmod(0o755)

            for item in temp_dir.rglob("*"):
                if item.is_file():
                    arcname = str(item.relative_to(temp_dir))
                    tar.add(item, arcname=arcname)

            shutil.rmtree(temp_dir)

        # Calcula o checksum do snapshot
        checksum = self._calculate_checksum(snapshot_path)

        metadata = self._load_metadata()
        metadata["snapshots"].append({
            "id": snapshot_id,
            "base_image": safe_image,
            "timestamp": datetime.datetime.now().isoformat(),
            "checksum": checksum
        })
        metadata["current"] = snapshot_id
        self._save_metadata(metadata)

        logger.info(f"Snapshot criado: {snapshot_id}")
        return snapshot_id

    def get_status(self) -> List[str]:
        """Retorna a lista de snapshots disponíveis."""
        metadata = self._load_metadata()
        return [s["id"] for s in metadata["snapshots"]]

    def get_current_snapshot(self) -> Optional[str]:
        """Retorna o snapshot atualmente ativo."""
        metadata = self._load_metadata()
        return metadata.get("current")

    def rollback_to_snapshot(self, snapshot_id: str) -> bool:
        """
        Realiza rollback para um snapshot específico.
        Na prática, atualiza o metadado 'current'.
        """
        logger.info(f"Iniciando rollback para: {snapshot_id}")
        
        safe_id = self._sanitize_filename(snapshot_id)
        
        metadata = self._load_metadata()
        snapshots_ids = [s["id"] for s in metadata["snapshots"]]
        if safe_id not in snapshots_ids:
            logger.error(f"Snapshot '{safe_id}' não encontrado nos metadados")
            raise ValueError(f"Snapshot '{safe_id}' não encontrado")

        snapshot_path = self.snapshots_dir / f"{safe_id}.tar.gz"
        if not snapshot_path.exists():
            logger.error(f"Arquivo do snapshot '{safe_id}' não encontrado")
            raise FileNotFoundError(f"Arquivo do snapshot '{safe_id}' não encontrado")

        # Verifica a integridade do snapshot
        expected_checksum = None
        for snap in metadata["snapshots"]:
            if snap["id"] == safe_id:
                expected_checksum = snap.get("checksum")
                break
        
        if expected_checksum:
            current_checksum = self._calculate_checksum(snapshot_path)
            if current_checksum != expected_checksum:
                logger.error(f"Checksum do snapshot '{safe_id}' não confere. Esperado: {expected_checksum}, Obtido: {current_checksum}")
                raise ValueError(f"Snapshot '{safe_id}' está corrompido")

        metadata["current"] = safe_id
        self._save_metadata(metadata)
        
        logger.info(f"Rollback concluído para: {safe_id}")
        return True
