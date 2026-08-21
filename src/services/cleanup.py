"""
Serviço para limpeza de snapshots.
"""

from pathlib import Path
from typing import Optional
from builder import SystemBuilder
from logger import get_logger
from exceptions import SnapshotNotFoundError

logger = get_logger()

class CleanupService:
    """Serviço para limpeza de snapshots."""
    
    def __init__(self, base_dir: Path):
        self.builder = SystemBuilder(base_dir)
    
    def cleanup(self, keep: int = 5, snapshot_id: Optional[str] = None) -> int:
        """
        Remove snapshots antigos.
        
        Args:
            keep: Número de snapshots a manter
            snapshot_id: ID específico para remover (opcional)
        
        Returns:
            Número de snapshots removidos
        """
        if snapshot_id:
            return self._remove_specific(snapshot_id)
        return self._remove_old(keep)
    
    def _remove_specific(self, snapshot_id: str) -> int:
        """Remove um snapshot específico."""
        logger.info(f"Removendo snapshot específico: {snapshot_id}")
        
        # Verifica se é o atual
        current = self.builder.get_current_snapshot()
        if snapshot_id == current:
            raise ValueError(f"Não é possível remover o snapshot atual: {snapshot_id}")
        
        # Remove o snapshot
        self.builder._remove_snapshot(snapshot_id)
        logger.info(f"Snapshot removido: {snapshot_id}")
        return 1
    
    def _remove_old(self, keep: int) -> int:
        """Remove snapshots antigos mantendo os N mais recentes."""
        snapshots = self.builder.get_status()
        if len(snapshots) <= keep:
            logger.info(f"Apenas {len(snapshots)} snapshots, nenhuma ação necessária")
            return 0
        
        # Ordena por timestamp
        def get_timestamp(snap_id):
            try:
                parts = snap_id.split('_')
                if len(parts) >= 3:
                    return parts[1] + parts[2]
            except:
                pass
            return "00000000000000"
        
        snapshots_ordenados = sorted(snapshots, key=get_timestamp, reverse=True)
        snapshots_para_remover = snapshots_ordenados[keep:]
        
        logger.info(f"Removendo {len(snapshots_para_remover)} snapshots antigos")
        for snap_id in snapshots_para_remover:
            self.builder._remove_snapshot(snap_id)
        
        return len(snapshots_para_remover)
