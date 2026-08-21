#!/usr/bin/env python3
"""
ProteusOS - SystemBuilder
Gerencia a criação e versionamento de snapshots (imagens atômicas) com suporte a diffs.
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
import subprocess

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
        self.diff_dir = self.base_dir / "diffs"
        self._ensure_directories()

    def _ensure_directories(self):
        """Cria os diretórios necessários."""
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self.diff_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Directories created in: {self.base_dir}")

    def _load_metadata(self) -> Dict:
        """Carrega os metadados dos snapshots com locking e recovery."""
        with file_lock(self.lock_file):
            if self.metadata_file.exists():
                try:
                    with open(self.metadata_file, 'r') as f:
                        return json.load(f)
                except json.JSONDecodeError as e:
                    logger.warning(f"Metadata file corrupted: {e}")
                    backup_file = self.metadata_file.with_suffix('.json.bak')
                    if backup_file.exists():
                        logger.info("Recovering metadata from backup...")
                        with open(backup_file, 'r') as f:
                            return json.load(f)
                    logger.error("Could not recover metadata. Creating new one.")
                    return {"snapshots": [], "current": None, "diffs": []}
            return {"snapshots": [], "current": None, "diffs": []}

    def _save_metadata(self, metadata: Dict):
        """Salva os metadados com backup automático e locking."""
        with file_lock(self.lock_file):
            if self.metadata_file.exists():
                shutil.copy2(self.metadata_file, self.metadata_file.with_suffix('.json.bak'))
                logger.debug("Metadata backup created")
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            logger.debug("Metadata saved successfully")

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

    def _create_diff(self, base_id: str, new_id: str) -> bool:
        """Cria um diff entre dois snapshots usando rsync."""
        base_path = self.snapshots_dir / f"{base_id}.tar.gz"
        new_path = self.snapshots_dir / f"{new_id}.tar.gz"
        diff_path = self.diff_dir / f"{base_id}--{new_id}.diff"

        if not base_path.exists() or not new_path.exists():
            logger.error("Base or new snapshot not found for diff.")
            return False

        try:
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdir:
                base_dir = Path(tmpdir) / "base"
                new_dir = Path(tmpdir) / "new"
                base_dir.mkdir()
                new_dir.mkdir()

                subprocess.run(["tar", "-xzf", str(base_path), "-C", str(base_dir)], check=True)
                subprocess.run(["tar", "-xzf", str(new_path), "-C", str(new_dir)], check=True)

                cmd = ["rsync", "-avn", "--delete", f"{base_dir}/", f"{new_dir}/"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                diff_content = result.stdout

                with open(diff_path, 'w') as f:
                    f.write(diff_content)

            return True
        except Exception as e:
            logger.error(f"Error creating diff: {e}")
            return False

    def snapshot_exists(self, snapshot_id: str) -> bool:
        """Verifica se um snapshot existe."""
        safe_id = self._sanitize_filename(snapshot_id)
        snapshot_path = self.snapshots_dir / f"{safe_id}.tar.gz"
        return snapshot_path.exists()

    def build_base(self, base_image: str, full: bool = True) -> str:
        """
        Constrói um sistema base a partir de uma imagem.
        Se full=True, cria um snapshot completo. Caso contrário, cria um diff.
        """
        logger.info(f"Building base image: {base_image}")

        safe_image = self._sanitize_filename(base_image)
        snapshot_id = self._generate_snapshot_id(safe_image)
        snapshot_path = self.snapshots_dir / f"{snapshot_id}.tar.gz"

        print(f"   Building base image '{safe_image}'...")

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

        checksum = self._calculate_checksum(snapshot_path)

        metadata = self._load_metadata()

        if not full and metadata["snapshots"]:
            last_snapshot = metadata["snapshots"][-1]["id"]
            self._create_diff(last_snapshot, snapshot_id)

        metadata["snapshots"].append({
            "id": snapshot_id,
            "base_image": safe_image,
            "timestamp": datetime.datetime.now().isoformat(),
            "checksum": checksum,
            "full": full,
            "parent": metadata["snapshots"][-1]["id"] if not full and metadata["snapshots"] else None
        })
        metadata["current"] = snapshot_id
        self._save_metadata(metadata)

        logger.info(f"Snapshot created: {snapshot_id}")
        return snapshot_id

    def get_status(self) -> List[str]:
        """Retorna a lista de snapshots disponíveis."""
        metadata = self._load_metadata()
        return [s["id"] for s in metadata["snapshots"]]

    def get_current_snapshot(self) -> Optional[str]:
        """Retorna o snapshot atualmente ativo."""
        metadata = self._load_metadata()
        return metadata.get("current")

    def rollback_to_snapshot(self, snapshot_id: str) -> str:
        """
        Realiza rollback para um snapshot específico.
        Retorna o ID do snapshot após o rollback.
        """
        logger.info(f"Rollback initiated to: {snapshot_id}")

        safe_id = self._sanitize_filename(snapshot_id)

        metadata = self._load_metadata()
        snapshots_ids = [s["id"] for s in metadata["snapshots"]]
        if safe_id not in snapshots_ids:
            logger.error(f"Snapshot '{safe_id}' not found in metadata")
            raise ValueError(f"Snapshot '{safe_id}' not found")

        snapshot_path = self.snapshots_dir / f"{safe_id}.tar.gz"
        if not snapshot_path.exists():
            logger.error(f"Snapshot file '{safe_id}' not found")
            raise FileNotFoundError(f"Snapshot file '{safe_id}' not found")

        expected_checksum = None
        for snap in metadata["snapshots"]:
            if snap["id"] == safe_id:
                expected_checksum = snap.get("checksum")
                break

        if expected_checksum:
            current_checksum = self._calculate_checksum(snapshot_path)
            if current_checksum != expected_checksum:
                logger.error(f"Checksum mismatch for snapshot '{safe_id}'.")
                raise ValueError(f"Snapshot '{safe_id}' is corrupted")

        metadata["current"] = safe_id
        self._save_metadata(metadata)

        logger.info(f"Rollback completed to: {safe_id}")
        return safe_id

    def _remove_snapshot(self, snapshot_id: str) -> bool:
        """Remove um snapshot (uso interno)."""
        safe_id = self._sanitize_filename(snapshot_id)
        snapshot_path = self.snapshots_dir / f"{safe_id}.tar.gz"
        
        if not snapshot_path.exists():
            return False
        
        # Remove o arquivo
        snapshot_path.unlink()
        
        # Remove dos metadados
        metadata = self._load_metadata()
        metadata["snapshots"] = [s for s in metadata["snapshots"] if s["id"] != safe_id]
        if metadata.get("current") == safe_id:
            metadata["current"] = None
        self._save_metadata(metadata)
        
        logger.info(f"Snapshot removed: {safe_id}")
        return True
