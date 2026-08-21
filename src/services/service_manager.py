"""
Serviço para gerenciamento de serviços.
"""

from init_manager import InitManager
from logger import get_logger
from exceptions import ServiceNotFoundError

logger = get_logger()

class ServiceManagerService:
    """Serviço para gerenciamento de serviços."""
    
    def __init__(self):
        self.manager = InitManager()
    
    def list(self):
        """Lista serviços ativos."""
        return self.manager.list_services()
    
    def start(self, service_name: str) -> bool:
        """Inicia um serviço."""
        logger.info(f"Iniciando serviço: {service_name}")
        result = self.manager.start_service(service_name)
        if not result:
            raise ServiceNotFoundError(f"Serviço '{service_name}' não encontrado")
        return result
    
    def stop(self, service_name: str) -> bool:
        """Para um serviço."""
        logger.info(f"Parando serviço: {service_name}")
        result = self.manager.stop_service(service_name)
        if not result:
            raise ServiceNotFoundError(f"Serviço '{service_name}' não encontrado")
        return result
    
    def enable(self, service_name: str) -> bool:
        """Habilita um serviço."""
        logger.info(f"Habilitando serviço: {service_name}")
        result = self.manager.enable_service(service_name)
        if not result:
            raise ServiceNotFoundError(f"Serviço '{service_name}' não encontrado")
        return result
    
    def disable(self, service_name: str) -> bool:
        """Desabilita um serviço."""
        logger.info(f"Desabilitando serviço: {service_name}")
        result = self.manager.disable_service(service_name)
        if not result:
            raise ServiceNotFoundError(f"Serviço '{service_name}' não encontrado")
        return result
