#!/usr/bin/env python3
"""
ProteusOS - PackageManager
Manages packages transactionally with dependency support.
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
        """Creates the necessary directories."""
        self.packages_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_filename(self, name: str) -> str:
        """Sanitizes a name for use in filenames."""
        if not name:
            return "unknown"
        sanitized = re.sub(ALLOWED_FILENAME_CHARS, '_', name)
        return sanitized[:255]

    def _load_installed(self) -> Dict:
        """Loads the list of installed packages with locking."""
        with file_lock(self.lock_file):
            if self.installed_file.exists():
                try:
                    with open(self.installed_file, 'r') as f:
                        return json.load(f)
                except json.JSONDecodeError:
                    logger.warning("Package file corrupted. Creating new one.")
                    return {"packages": []}
            return {"packages": []}

    def _save_installed(self, data: Dict):
        """Saves the list of installed packages with backup and locking."""
        with file_lock(self.lock_file):
            if self.installed_file.exists():
                shutil.copy2(self.installed_file, self.installed_file.with_suffix('.json.bak'))
            with open(self.installed_file, 'w') as f:
                json.dump(data, f, indent=2)

    def _get_installed_ids(self) -> Set[str]:
        """Returns a set with the IDs of installed packages."""
        installed = self._load_installed()
        return {pkg["id"] for pkg in installed["packages"]}

    def _check_dependencies(self, dependencies: Dict) -> bool:
        """Checks if all dependencies are installed."""
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
        Installs a package and its dependencies atomically.
        The package must be a .tar.gz file with metadata.
        """
        package_path = Path(package_path)
        if not package_path.exists():
            raise FileNotFoundError(f"Package not found: {package_path}")

        logger.info(f"Installing package: {package_path}")

        temp_dir = Path(tempfile.mkdtemp(prefix="proteus_pkg_"))
        try:
            with tarfile.open(package_path, "r:gz") as tar:
                tar.extractall(temp_dir)

            metadata_file = temp_dir / "package.json"
            if not metadata_file.exists():
                raise ValueError("Invalid package: package.json not found")

            with open(metadata_file, 'r') as f:
                metadata = json.load(f)

            pkg_name = self._sanitize_filename(metadata.get("name", "unknown"))

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
                    f"Unsatisfied dependencies: {', '.join(missing)}. "
                    f"Use force=True to install anyway."
                )

            pkg_id = f"{PACKAGE_PREFIX}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

            pkg_dir = self.packages_dir / pkg_id
            shutil.copytree(temp_dir, pkg_dir)

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

        logger.info(f"Package installed successfully: {pkg_id}")
        return pkg_id

    def list_packages(self) -> List[str]:
        """Lists installed packages with their dependencies."""
        installed = self._load_installed()
        result = []
        for pkg in installed["packages"]:
            deps = pkg.get("dependencies", {})
            deps_str = ", ".join([f"{k}=={v}" for k, v in deps.items()]) if deps else "none"
            result.append(f"{pkg['name']} (v{pkg['version']}) - ID: {pkg['id']} - Deps: [{deps_str}]")
        return result

    def uninstall(self, package_id: str, recursive: bool = False) -> str:
        """
        Uninstalls a package.
        If recursive=True, also uninstalls packages that depend on it.
        """
        logger.info(f"Uninstalling package: {package_id}")

        installed = self._load_installed()
        
        pkg_index = None
        pkg_data = None
        for i, pkg in enumerate(installed["packages"]):
            if pkg["id"] == package_id:
                pkg_index = i
                pkg_data = pkg
                break

        if pkg_index is None:
            raise ValueError(f"Package '{package_id}' not found")

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

        logger.info(f"Package uninstalled: {removed_pkg['name']}")
        return removed_pkg["name"]
