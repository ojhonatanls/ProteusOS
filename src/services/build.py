"""
Serviço para operações de build.
"""

from pathlib import Path
from typing import Optional
from builder import SystemBuilder
from logger import get_logger
from exceptions import ToolNotFoundError

logger = get_logger()

class BuildService:
    """Serviço para operações de build."""
    
    def __init__(self, base_dir: Path):
        self.builder = SystemBuilder(base_dir)
    
    def build(self, base_image: str, use_c: bool = False, full: bool = True) -> str:
        """
        Constrói um snapshot.
        
        Args:
            base_image: Nome da imagem base (alpine, debian)
            use_c: Usar módulo C (experimental)
            full: Criar snapshot completo (True) ou diff (False)
        
        Returns:
            ID do snapshot criado
        """
        logger.info(f"Build iniciado: {base_image} (full={full}, use_c={use_c})")
        
        if use_c:
            try:
                import snapshot
                result = snapshot.build(base_image)
                logger.info(f"Build concluído com C: {result}")
                return result
            except ImportError:
                logger.warning("Módulo C não disponível, usando Python")
            except Exception as e:
                logger.error(f"Erro no módulo C: {e}")
                logger.info("Usando fallback para Python")
        
        result = self.builder.build_base(base_image, full=full)
        logger.info(f"Build concluído: {result}")
        return result
