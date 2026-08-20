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
from pathlib import Path
from typing import List, Dict

class SystemBuilder:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.snapshots_dir = self.base_dir / "snapshots"
        self.metadata_file = self.base_dir / "metadata.json"
        self._ensure_directories()

    def _ensure_directories(self):
        """Cria os diretórios necessários."""
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

    def _load_metadata(self) -> Dict:
        """Carrega os metadados dos snapshots."""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {"snapshots": [], "current": None}

    def _save_metadata(self, metadata: Dict):
        """Salva os metadados."""
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

    def _generate_snapshot_id(self, base_image: str) -> str:
        """Gera um ID único para o snapshot."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"snapshot_{timestamp}_{base_image}"

    def snapshot_exists(self, snapshot_id: str) -> bool:
        """Verifica se um snapshot existe."""
        snapshot_path = self.snapshots_dir / f"{snapshot_id}.tar.gz"
        return snapshot_path.exists()

    def build_base(self, base_image: str) -> str:
        """
        Constrói um sistema base a partir de uma imagem.
        Na prática, cria um snapshot com uma estrutura de diretórios simulada.
        """
        snapshot_id = self._generate_snapshot_id(base_image)
        snapshot_path = self.snapshots_dir / f"{snapshot_id}.tar.gz"

        # Cria um snapshot de exemplo (simula a construção)
        print(f"   Construindo imagem base '{base_image}'...")
        with tarfile.open(snapshot_path, "w:gz") as tar:
            # Cria uma estrutura de diretórios simulada
            temp_dir = self.base_dir / "temp_build"
            temp_dir.mkdir(exist_ok=True)

            # Cria alguns arquivos simulados
            (temp_dir / "etc").mkdir(exist_ok=True)
            (temp_dir / "etc" / "os-release").write_text(f"ID=proteus\nVERSION={base_image}\n")
            (temp_dir / "bin").mkdir(exist_ok=True)
            (temp_dir / "bin" / "sh").write_text("#!/bin/sh\necho 'ProteusOS Shell'", encoding='utf-8')
            (temp_dir / "bin" / "sh").chmod(0o755)

            # Adiciona ao tar
            for item in temp_dir.rglob("*"):
                if item.is_file():
                    arcname = str(item.relative_to(temp_dir))
                    tar.add(item, arcname=arcname)

            # Remove o diretório temporário
            shutil.rmtree(temp_dir)

        # Atualiza metadados
        metadata = self._load_metadata()
        metadata["snapshots"].append({
            "id": snapshot_id,
            "base_image": base_image,
            "timestamp": datetime.datetime.now().isoformat()
        })
        metadata["current"] = snapshot_id
        self._save_metadata(metadata)

        return snapshot_id

    def get_status(self) -> List[str]:
        """Retorna a lista de snapshots disponíveis."""
        metadata = self._load_metadata()
        return [s["id"] for s in metadata["snapshots"]]

    def get_current_snapshot(self) -> str:
        """Retorna o snapshot atualmente ativo."""
        metadata = self._load_metadata()
        return metadata.get("current")

    def rollback_to_snapshot(self, snapshot_id: str) -> bool:
        """
        Realiza rollback para um snapshot específico.
        Na prática, atualiza o metadado 'current'.
        """
        metadata = self._load_metadata()
        snapshots_ids = [s["id"] for s in metadata["snapshots"]]
        if snapshot_id not in snapshots_ids:
            raise ValueError(f"Snapshot '{snapshot_id}' não encontrado")

        metadata["current"] = snapshot_id
        self._save_metadata(metadata)
        return True
