"""
Testes de integração do ProteusOS.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import os

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from builder import SystemBuilder
from pkg_manager import PackageManager
from updater import SystemUpdater
from services import BuildService, SnapshotService, PackageService

class TestIntegrationFlow(unittest.TestCase):
    """Testa fluxos completos do ProteusOS."""
    
    def setUp(self):
        """Configura ambiente de teste."""
        self.test_dir = Path(tempfile.mkdtemp(prefix="proteus_test_"))
        self.builder = SystemBuilder(self.test_dir)
        self.pkg_manager = PackageManager(self.test_dir)
        self.updater = SystemUpdater(self.test_dir)
        self.build_service = BuildService(self.test_dir)
        self.snapshot_service = SnapshotService(self.test_dir)
        self.package_service = PackageService(self.test_dir)
    
    def tearDown(self):
        """Limpa ambiente de teste."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_full_flow(self):
        """Testa fluxo completo: build -> status -> rollback."""
        # 1. Criar snapshot
        snap1 = self.build_service.build("alpine", full=True)
        self.assertIsNotNone(snap1)
        
        # 2. Verificar status
        snapshots, current = self.snapshot_service.get_status()
        self.assertIn(snap1, snapshots)
        self.assertEqual(current, snap1)
        
        # 3. Criar segundo snapshot
        snap2 = self.build_service.build("debian", full=True)
        self.assertIsNotNone(snap2)
        
        # 4. Verificar status
        snapshots, current = self.snapshot_service.get_status()
        self.assertIn(snap2, snapshots)
        self.assertEqual(current, snap2)
        
        # 5. Rollback para o primeiro
        result = self.snapshot_service.rollback(snap1)
        self.assertEqual(result, snap1)
        
        # 6. Verificar status após rollback
        _, current = self.snapshot_service.get_status()
        self.assertEqual(current, snap1)

if __name__ == "__main__":
    unittest.main()
