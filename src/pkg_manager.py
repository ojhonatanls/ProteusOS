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
from pathlib import Path
from typing import List, Dict, Set
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

    def _get_installed_ids(self) -> Set[str]:
        """Retorna um set com os IDs dos pacotes instalados."""
        installed = self._load_installed()
        return {pkg["id"] for pkg in installed["packages"]}

    def install(self, package_path: str, force: bool = False) -> str:
        """
        Instala um pacote e suas dependências de forma atômica.
        O pacote deve ser um arquivo .tar.gz com metadados.
        """
        package_path = Path(package_path)
        if not package_path.exists():
            raise FileNotFoundError(f"Pacote não encontrado: {package_path}")

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

            # Verifica dependências
            dependencies = metadata.get("dependencies", {})
            installed_ids = self._get_installed_ids()
            
            # Se não for força, verifica se todas as dependências estão instaladas
            if not force:
                missing_deps = []
                for dep_name, dep_version in dependencies.items():
                    # Procura por um pacote com este nome instalado
                    installed = self._load_installed()
                    found = False
                    for pkg in installed["packages"]:
                        if pkg.get("name") == dep_name and pkg.get("version") == dep_version:
                            found = True
                            break
                    if not found:
                        missing_deps.append(f"{dep_name}=={dep_version}")
                
                if missing_deps:
                    raise ValueError(
                        f"Dependências não satisfeitas: {', '.join(missing_deps)}. "
                        f"Use force=True para instalar mesmo assim."
                    )

            # Gera um ID único para o pacote
            pkg_id = f"pkg_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Copia o pacote para o diretório de pacotes
            pkg_dir = self.packages_dir / pkg_id
            shutil.copytree(temp_dir, pkg_dir)

            # Atualiza a lista de pacotes instalados
            installed = self._load_installed()
            installed["packages"].append({
                "id": pkg_id,
                "name": metadata.get("name", "unknown"),
                "version": metadata.get("version", "1.0"),
                "dependencies": dependencies,
                "timestamp": datetime.datetime.now().isoformat()
            })
            self._save_installed(installed)

        finally:
            # Limpa o diretório temporário
            shutil.rmtree(temp_dir, ignore_errors=True)

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
        installed = self._load_installed()
        
        # Encontra o índice do pacote
        pkg_index = None
        pkg_data = None
        for i, pkg in enumerate(installed["packages"]):
            if pkg["id"] == package_id:
                pkg_index = i
                pkg_data = pkg
                break

        if pkg_index is None:
            raise ValueError(f"Pacote '{package_id}' não encontrado")

        # Se recursive, verifica se algum pacote depende deste
        if recursive:
            dependents = []
            for pkg in installed["packages"]:
                deps = pkg.get("dependencies", {})
                if pkg_data["name"] in deps:
                    dependents.append(pkg["id"])
            
            if dependents:
                # Desinstala os dependentes primeiro
                for dep_id in dependents:
                    self.uninstall(dep_id, recursive=True)

        # Remove o diretório do pacote
        pkg_dir = self.packages_dir / package_id
        if pkg_dir.exists():
            shutil.rmtree(pkg_dir)

        # Remove da lista
        removed_pkg = installed["packages"].pop(pkg_index)
        self._save_installed(installed)

        return removed_pkg["name"]