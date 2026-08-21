"""
Serviço para operações com snapshots.
"""

from pathlib import Path
from typing import Optional, List, Tuple
from builder import SystemBuilder
from logger import get_logger
from exceptions import SnapshotNotFoundError

logger = get_logger()

class SnapshotService:
    """Serviço para operações com snapshots."""
    
    def __init__(self, base_dir: Path):
        self.builder = SystemBuilder(base_dir)
    
    def get_status(self) -> Tuple[List[str], Optional[str]]:
        """Retorna lista de snapshots e o atual."""
        return self.builder.get_status(), self.builder.get_current_snapshot()
    
    def rollback(self, snapshot_id: Optional[str] = None) -> str:
        """
        Realiza rollback para um snapshot.
        
        Args:
            snapshot_id: ID do snapshot (opcional, usa penúltimo se não especificado)
        
        Returns:
            ID do snapshot após rollback
        """
        if snapshot_id:
            logger.info(f"Rollback iniciado: {snapshot_id}")
            result = self.builder.rollback_to_snapshot(snapshot_id)
            logger.info(f"Rollback concluído: {result}")
            return result
        
        # Rollback para o penúltimo snapshot
        snapshots = self.builder.get_status()
        if len(snapshots) < 2:
            raise SnapshotNotFoundError("Não há snapshots suficientes para rollback")
        
        target = snapshots[-2]
        logger.info(f"Rollback para penúltimo snapshot: {target}")
        result = self.builder.rollback_to_snapshot(target)
        logger.info(f"Rollback concluído: {result}")
        return result
