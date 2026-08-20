#!/usr/bin/env python3
"""
ProteusOS - PackageManager
Gerencia pacotes de forma transacional com suporte a dependências.
"""

import os
import shutil
import json
import tarfile
import tempfile
import re
from pathlib import Path
from typing import List, Dict, Set
import datetime

from constants import PACKAGES_DIR, PACKAGE_PREFIX, ALLOWED_FILENAME_CHARS
from logger import get_logger
from locking import file_lock

logger = get_logger()

class PackageManager:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.packages_dir = self.base_dir / PACKAGES_DIR
        self.installed_file = self.base_dir / "installed_packages.json"
        self.lock_file = self.base_dir / "packages.lock"
        self._ensure_directories()

    def _ensure_directories(self):
        """Cria os diretórios necessários."""
        self.packages_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_filename(self, name: str) -> str:
        """Sanitiza um nome para uso em nomes de arquivos."""
        if not name:
            return "unknown"
        sanitized = re.sub(ALLOWED_FILENAME_CHARS, '_', name)
        return sanitized[:255]  # Limita o tamanho

    def _load_installed(self) -> Dict:
        """Carrega a lista de pacotes instalados com locking."""
        with file_lock(self.lock_file):
            if self.installed_file.exists():
                try:
                    with open(self.installed_file, 'r') as f:
                        return json.load(f)
                except json.JSONDecodeError:
                    logger.warning("Arquivo de pacotes corrompido. Criando novo.")
                    return {"packages": []}
            return {"packages": []}

    def _save_installed(self, data: Dict):
        """Salva a lista de pacotes instalados com backup e locking."""
        with file_lock(self.lock_file):
            if self.installed_file.exists():
                shutil.copy2(self.installed_file, self.installed_file.with_suffix('.json.bak'))
            with open(self.installed_file, 'w') as f:
                json.dump(data, f, indent=2)

    def _get_installed_ids(self) -> Set[str]:
        """Retorna um set com os IDs dos pacotes instalados."""
        installed = self._load_installed()
        return {pkg["id"] for pkg in installed["packages"]}

    def _check_dependencies(self, dependencies: Dict) -> bool:
        """Verifica se todas as dependências estão instaladas."""
        installed = self._load_installed()
        for dep_name, dep_version in dependencies.items():
            found = False
            for pkg in installed["packages"]:
                if pkg.get("name") == dep_name and pkg.get("version") == dep_version:
                    found = True
                    break
            if not found:
                return False
        return True

    def install(self, package_path: str, force: bool = False) -> str:
        """
        Instala um pacote e suas dependências de forma atômica.
        O pacote deve ser um arquivo .tar.gz com metadados.
        """
        package_path = Path(package_path)
        if not package_path.exists():
            raise FileNotFoundError(f"Pacote não encontrado: {package_path}")

        logger.info(f"Instalando pacote: {package_path}")

        # Extrai o pacote em um diretório temporário
        temp_dir = Path(tempfile.mkdtemp(prefix="proteus_pkg_"))
        try:
            with tarfile.open(package_path, "r:gz") as tar:
                tar.extractall(temp_dir)

            # Verifica metadados
            metadata_file = temp_dir / "package.json"
            if not metadata_file.exists():
                raise ValueError("Pacote inválido: package.json não encontrado")

            with open(metadata_file, 'r') as f:
                metadata = json.load(f)

            # Sanitiza nome do pacote
            pkg_name = self._sanitize_filename(metadata.get("name", "unknown"))

            # Verifica dependências
            dependencies = metadata.get("dependencies", {})
            if not force and not self._check_dependencies(dependencies):
                missing = []
                installed = self._load_installed()
                for dep_name, dep_version in dependencies.items():
                    found = False
                    for pkg in installed["packages"]:
                        if pkg.get("name") == dep_name and pkg.get("version") == dep_version:
                            found = True
                            break
                    if not found:
                        missing.append(f"{dep_name}=={dep_version}")
                raise ValueError(
                    f"Dependências não satisfeitas: {', '.join(missing)}. "
                    f"Use force=True para instalar mesmo assim."
                )

            # Gera um ID único para o pacote
            pkg_id = f"{PACKAGE_PREFIX}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Copia o pacote para o diretório de pacotes
            pkg_dir = self.packages_dir / pkg_id
            shutil.copytree(temp_dir, pkg_dir)

            # Atualiza a lista de pacotes instalados
            installed = self._load_installed()
            installed["packages"].append({
                "id": pkg_id,
                "name": pkg_name,
                "version": metadata.get("version", "1.0"),
                "dependencies": dependencies,
                "timestamp": datetime.datetime.now().isoformat()
            })
            self._save_installed(installed)

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        logger.info(f"Pacote instalado com sucesso: {pkg_id}")
        return pkg_id

    def list_packages(self) -> List[str]:
        """Lista os pacotes instalados com suas dependências."""
        installed = self._load_installed()
        result = []
        for pkg in installed["packages"]:
            deps = pkg.get("dependencies", {})
            deps_str = ", ".join([f"{k}=={v}" for k, v in deps.items()]) if deps else "nenhuma"
            result.append(f"{pkg['name']} (v{pkg['version']}) - ID: {pkg['id']} - Deps: [{deps_str}]")
        return result

    def uninstall(self, package_id: str, recursive: bool = False) -> str:
        """
        Desinstala um pacote.
        Se recursive=True, desinstala também os pacotes que dependem dele.
        """
        logger.info(f"Desinstalando pacote: {package_id}")

        installed = self._load_installed()
        
        pkg_index = None
        pkg_data = None
        for i, pkg in enumerate(installed["packages"]):
            if pkg["id"] == package_id:
                pkg_index = i
                pkg_data = pkg
                break

        if pkg_index is None:
            raise ValueError(f"Pacote '{package_id}' não encontrado")

        if recursive:
            dependents = []
            for pkg in installed["packages"]:
                deps = pkg.get("dependencies", {})
                if pkg_data["name"] in deps:
                    dependents.append(pkg["id"])
            for dep_id in dependents:
                self.uninstall(dep_id, recursive=True)

        pkg_dir = self.packages_dir / package_id
        if pkg_dir.exists():
            shutil.rmtree(pkg_dir)

        removed_pkg = installed["packages"].pop(pkg_index)
        self._save_installed(installed)

        logger.info(f"Pacote desinstalado: {removed_pkg['name']}")
        return removed_pkg["name"]
