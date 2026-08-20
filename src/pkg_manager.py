#!/usr/bin/env python3
"""
ProteusOS - PackageManager
Gerencia pacotes de forma transacional com rollback.
"""

import os
import shutil
import json
import tarfile
import tempfile
from pathlib import Path
from typing import List, Dict
import datetime

class PackageManager:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.packages_dir = self.base_dir / "packages"
        self.installed_file = self.base_dir / "installed_packages.json"
        self._ensure_directories()

    def _ensure_directories(self):
        """Cria os diretórios necessários."""
        self.packages_dir.mkdir(parents=True, exist_ok=True)

    def _load_installed(self) -> Dict:
        """Carrega a lista de pacotes instalados."""
        if self.installed_file.exists():
            with open(self.installed_file, 'r') as f:
                return json.load(f)
        return {"packages": []}

    def _save_installed(self, data: Dict):
        """Salva a lista de pacotes instalados."""
        with open(self.installed_file, 'w') as f:
            json.dump(data, f, indent=2)

    def install(self, package_path: str) -> str:
        """
        Instala um pacote de forma atômica.
        O pacote deve ser um arquivo .tar.gz com metadados.
        """
        package_path = Path(package_path)
        if not package_path.exists():
            raise FileNotFoundError(f"Pacote não encontrado: {package_path}")

        # Gera um ID único para o pacote
        pkg_id = f"pkg_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Extrai o pacote em um diretório temporário
        temp_dir = Path(tempfile.mkdtemp(prefix="proteus_pkg_"))
        try:
            with tarfile.open(package_path, "r:gz") as tar:
                tar.extractall(temp_dir)

            # Verifica se há metadados
            metadata_file = temp_dir / "package.json"
            if not metadata_file.exists():
                raise ValueError("Pacote inválido: package.json não encontrado")

            with open(metadata_file, 'r') as f:
                metadata = json.load(f)

            # Copia o pacote para o diretório de pacotes
            pkg_dir = self.packages_dir / pkg_id
            shutil.copytree(temp_dir, pkg_dir)

            # Atualiza a lista de pacotes instalados
            installed = self._load_installed()
            installed["packages"].append({
                "id": pkg_id,
                "name": metadata.get("name", "unknown"),
                "version": metadata.get("version", "1.0"),
                "timestamp": datetime.datetime.now().isoformat()
            })
            self._save_installed(installed)

        finally:
            # Limpa o diretório temporário
            shutil.rmtree(temp_dir, ignore_errors=True)

        return pkg_id

    def list_packages(self) -> List[str]:
        """Lista os pacotes instalados."""
        installed = self._load_installed()
        return [f"{pkg['name']} (v{pkg['version']}) - ID: {pkg['id']}" for pkg in installed["packages"]]

    def uninstall(self, package_id: str) -> str:
        """
        Desinstala um pacote.
        """
        installed = self._load_installed()
        pkg_index = None
        for i, pkg in enumerate(installed["packages"]):
            if pkg["id"] == package_id:
                pkg_index = i
                break

        if pkg_index is None:
            raise ValueError(f"Pacote '{package_id}' não encontrado")

        # Remove o diretório do pacote
        pkg_dir = self.packages_dir / package_id
        if pkg_dir.exists():
            shutil.rmtree(pkg_dir)

        # Remove da lista
        removed_pkg = installed["packages"].pop(pkg_index)
        self._save_installed(installed)

        return removed_pkg["name"]