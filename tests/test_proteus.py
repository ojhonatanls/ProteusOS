#!/usr/bin/env python3
"""
Testes automatizados para o ProteusOS.
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
import sys
import os

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from builder import SystemBuilder
from pkg_manager import PackageManager
from updater import SystemUpdater

class TestProteusOS(unittest.TestCase):
    def setUp(self):
        """Configura um ambiente de teste temporário."""
        self.test_dir = Path(tempfile.mkdtemp(prefix="proteus_test_"))
        self.builder = SystemBuilder(self.test_dir)
        self.pkg_manager = PackageManager(self.test_dir)
        self.updater = SystemUpdater(self.test_dir)

    def tearDown(self):
        """Limpa o ambiente de teste."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_build_snapshot(self):
        """Testa a criação de um snapshot."""
        snapshot_id = self.builder.build_base("alpine")
        self.assertIsNotNone(snapshot_id)
        self.assertTrue(snapshot_id.startswith("snapshot_"))
        self.assertIn(snapshot_id, self.builder.get_status())

    def test_install_package(self):
        """Testa a instalação de um pacote."""
        # Cria um pacote de teste
        pkg_dir = self.test_dir / "test_pkg"
        pkg_dir.mkdir()
        (pkg_dir / "package.json").write_text(
            json.dumps({"name": "test", "version": "1.0"})
        )
        (pkg_dir / "test.sh").write_text("echo 'test'")
        
        pkg_tar = self.test_dir / "test.tar.gz"
        import tarfile
        with tarfile.open(pkg_tar, "w:gz") as tar:
            tar.add(pkg_dir, arcname=".")

        # Instala o pacote
        pkg_id = self.pkg_manager.install(str(pkg_tar))
        self.assertIsNotNone(pkg_id)
        self.assertTrue(pkg_id.startswith("pkg_"))

        # Verifica se foi listado
        packages = self.pkg_manager.list_packages()
        self.assertTrue(any("test" in pkg for pkg in packages))

    def test_rollback(self):
        """Testa o rollback para um snapshot."""
        # Cria dois snapshots
        snap1 = self.builder.build_base("alpine")
        snap2 = self.builder.build_base("debian")
        
        # Faz rollback para o primeiro
        result = self.updater.rollback(snap1)
        self.assertEqual(result, snap1)
        self.assertEqual(self.builder.get_current_snapshot(), snap1)

    def test_update(self):
        """Testa a aplicação de uma atualização."""
        # Cria um snapshot base
        self.builder.build_base("alpine")
        
        # Cria um pacote de atualização
        update_dir = self.test_dir / "update"
        update_dir.mkdir()
        (update_dir / "update.sh").write_text("echo 'update'")
        
        update_tar = self.test_dir / "update.tar.gz"
        import tarfile
        with tarfile.open(update_tar, "w:gz") as tar:
            tar.add(update_dir, arcname=".")

        # Aplica a atualização
        result = self.updater.apply_update(str(update_tar))
        self.assertIsNotNone(result)
        self.assertTrue(result.startswith("snapshot_"))

if __name__ == "__main__":
    unittest.main()
