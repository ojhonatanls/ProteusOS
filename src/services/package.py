"""
Serviço para operações com pacotes.
"""

from pathlib import Path
from typing import List
from pkg_manager import PackageManager
from logger import get_logger
from exceptions import PackageNotFoundError

logger = get_logger()

class PackageService:
    """Serviço para operações com pacotes."""
    
    def __init__(self, base_dir: Path):
        self.pkg_manager = PackageManager(base_dir)
    
    def install(self, package_path: str, force: bool = False) -> str:
        """Instala um pacote."""
        logger.info(f"Instalação de pacote: {package_path}")
        result = self.pkg_manager.install(package_path, force)
        logger.info(f"Pacote instalado: {result}")
        return result
    
    def list(self) -> List[str]:
        """Lista pacotes instalados."""
        return self.pkg_manager.list_packages()
    
    def uninstall(self, package_id: str) -> str:
        """Desinstala um pacote."""
        logger.info(f"Desinstalação de pacote: {package_id}")
        result = self.pkg_manager.uninstall(package_id)
        logger.info(f"Pacote desinstalado: {result}")
        return result
