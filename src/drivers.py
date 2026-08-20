#!/usr/bin/env python3
"""
ProteusOS - Drivers para Gerenciadores de Pacotes (APT, DNF, Pacman)
"""

import subprocess
import platform
from typing import List, Optional
from pathlib import Path

from logger import get_logger

logger = get_logger()


class PackageDriver:
    """Classe base para todos os drivers."""

    def __init__(self):
        self.name = "base"

    def install(self, package_name: str) -> bool:
        raise NotImplementedError

    def remove(self, package_name: str) -> bool:
        raise NotImplementedError

    def list_installed(self) -> List[str]:
        raise NotImplementedError

    def search(self, query: str) -> List[str]:
        raise NotImplementedError


class AptDriver(PackageDriver):
    """Driver para o APT (Debian/Ubuntu)."""

    def __init__(self):
        super().__init__()
        self.name = "apt"

    def install(self, package_name: str) -> bool:
        try:
            logger.info(f"[APT] Instalando: {package_name}")
            subprocess.run(
                ["sudo", "apt", "install", "-y", package_name],
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"[APT] Erro ao instalar {package_name}: {e.stderr.decode()}")
            return False

    def remove(self, package_name: str) -> bool:
        try:
            logger.info(f"[APT] Removendo: {package_name}")
            subprocess.run(
                ["sudo", "apt", "remove", "-y", package_name],
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"[APT] Erro ao remover {package_name}: {e.stderr.decode()}")
            return False

    def list_installed(self) -> List[str]:
        try:
            result = subprocess.run(
                ["dpkg", "-l"],
                capture_output=True,
                text=True,
                check=True
            )
            lines = result.stdout.splitlines()
            packages = []
            for line in lines:
                if line.startswith("ii"):
                    parts = line.split()
                    if len(parts) >= 2:
                        packages.append(parts[1])
            return packages
        except subprocess.CalledProcessError as e:
            logger.error(f"[APT] Erro ao listar pacotes: {e}")
            return []

    def search(self, query: str) -> List[str]:
        try:
            result = subprocess.run(
                ["apt-cache", "search", query],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.splitlines()
        except subprocess.CalledProcessError as e:
            logger.error(f"[APT] Erro ao buscar {query}: {e}")
            return []


class DnfDriver(PackageDriver):
    """Driver para o DNF (Fedora/RHEL)."""

    def __init__(self):
        super().__init__()
        self.name = "dnf"

    def install(self, package_name: str) -> bool:
        try:
            logger.info(f"[DNF] Instalando: {package_name}")
            subprocess.run(
                ["sudo", "dnf", "install", "-y", package_name],
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"[DNF] Erro ao instalar {package_name}: {e.stderr.decode()}")
            return False

    def remove(self, package_name: str) -> bool:
        try:
            logger.info(f"[DNF] Removendo: {package_name}")
            subprocess.run(
                ["sudo", "dnf", "remove", "-y", package_name],
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"[DNF] Erro ao remover {package_name}: {e.stderr.decode()}")
            return False

    def list_installed(self) -> List[str]:
        try:
            result = subprocess.run(
                ["dnf", "list", "installed"],
                capture_output=True,
                text=True,
                check=True
            )
            lines = result.stdout.splitlines()
            packages = []
            for line in lines:
                if line and not line.startswith("Installed"):
                    parts = line.split()
                    if parts:
                        packages.append(parts[0])
            return packages
        except subprocess.CalledProcessError as e:
            logger.error(f"[DNF] Erro ao listar pacotes: {e}")
            return []

    def search(self, query: str) -> List[str]:
        try:
            result = subprocess.run(
                ["dnf", "search", query],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.splitlines()
        except subprocess.CalledProcessError as e:
            logger.error(f"[DNF] Erro ao buscar {query}: {e}")
            return []


class PacmanDriver(PackageDriver):
    """Driver para o Pacman (Arch Linux)."""

    def __init__(self):
        super().__init__()
        self.name = "pacman"

    def install(self, package_name: str) -> bool:
        try:
            logger.info(f"[PACMAN] Instalando: {package_name}")
            subprocess.run(
                ["sudo", "pacman", "-S", "--noconfirm", package_name],
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"[PACMAN] Erro ao instalar {package_name}: {e.stderr.decode()}")
            return False

    def remove(self, package_name: str) -> bool:
        try:
            logger.info(f"[PACMAN] Removendo: {package_name}")
            subprocess.run(
                ["sudo", "pacman", "-R", "--noconfirm", package_name],
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"[PACMAN] Erro ao remover {package_name}: {e.stderr.decode()}")
            return False

    def list_installed(self) -> List[str]:
        try:
            result = subprocess.run(
                ["pacman", "-Q"],
                capture_output=True,
                text=True,
                check=True
            )
            lines = result.stdout.splitlines()
            packages = []
            for line in lines:
                if line:
                    parts = line.split()
                    if parts:
                        packages.append(parts[0])
            return packages
        except subprocess.CalledProcessError as e:
            logger.error(f"[PACMAN] Erro ao listar pacotes: {e}")
            return []

    def search(self, query: str) -> List[str]:
        try:
            result = subprocess.run(
                ["pacman", "-Ss", query],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.splitlines()
        except subprocess.CalledProcessError as e:
            logger.error(f"[PACMAN] Erro ao buscar {query}: {e}")
            return []


class PackageOrchestrator:
    """Orquestrador que escolhe o driver certo."""

    def __init__(self):
        self.drivers = {
            "apt": AptDriver(),
            "dnf": DnfDriver(),
            "pacman": PacmanDriver()
        }
        self.logger = get_logger()

    def install(self, package_name: str, driver_name: Optional[str] = None) -> bool:
        """Instala um pacote usando o driver especificado ou detectando automaticamente."""
        driver = self._get_driver(package_name, driver_name)
        if not driver:
            self.logger.error(f"Driver não encontrado para: {package_name}")
            return False

        self.logger.info(f"🔄 Instalando {package_name} via {driver.name}")

        # 1. Cria snapshot antes
        from builder import SystemBuilder
        builder = SystemBuilder(Path.home() / "proteus_os")
        snapshot_id = builder.build_base("pre-install")

        # 2. Executa a instalação
        success = driver.install(package_name)

        if success:
            self.logger.info(f"✅ Instalação de {package_name} bem-sucedida")
            builder.build_base(f"post-install-{package_name}")
        else:
            self.logger.error(f"❌ Falha na instalação de {package_name}")
            builder.rollback_to_snapshot(snapshot_id)
            self.logger.info(f"↩️ Rollback realizado para {snapshot_id}")

        return success

    def remove(self, package_name: str, driver_name: Optional[str] = None) -> bool:
        """Remove um pacote usando o driver especificado ou detectando automaticamente."""
        driver = self._get_driver(package_name, driver_name)
        if not driver:
            self.logger.error(f"Driver não encontrado para: {package_name}")
            return False

        self.logger.info(f"🗑️ Removendo {package_name} via {driver.name}")
        return driver.remove(package_name)

    def list_installed(self, driver_name: Optional[str] = None) -> List[str]:
        """Lista pacotes instalados usando o driver especificado ou o padrão do sistema."""
        driver = self._get_driver("", driver_name)
        if not driver:
            self.logger.error("Driver não encontrado")
            return []
        return driver.list_installed()

    def search(self, query: str, driver_name: Optional[str] = None) -> List[str]:
        """Busca pacotes usando o driver especificado ou o padrão do sistema."""
        driver = self._get_driver("", driver_name)
        if not driver:
            self.logger.error("Driver não encontrado")
            return []
        return driver.search(query)

    def _get_driver(self, package_name: str, driver_name: Optional[str] = None) -> Optional[PackageDriver]:
        """Retorna o driver apropriado."""
        if driver_name and driver_name in self.drivers:
            return self.drivers[driver_name]

        # Detecção automática baseada na extensão do pacote
        if package_name.endswith(".deb"):
            return self.drivers["apt"]
        elif package_name.endswith(".rpm"):
            return self.drivers["dnf"]
        elif package_name.endswith(".pkg.tar.zst"):
            return self.drivers["pacman"]

        # Fallback: detectar o sistema operacional
        system = platform.system().lower()
        if system == "linux":
            try:
                with open("/etc/os-release") as f:
                    os_info = f.read().lower()
                    if "debian" in os_info or "ubuntu" in os_info:
                        return self.drivers["apt"]
                    elif "fedora" in os_info or "rhel" in os_info:
                        return self.drivers["dnf"]
                    elif "arch" in os_info:
                        return self.drivers["pacman"]
            except FileNotFoundError:
                pass

        # Default: apt
        self.logger.warning("Sistema não detectado, usando APT como fallback")
        return self.drivers["apt"]
