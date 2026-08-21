#!/usr/bin/env python3
"""
ProteusOS - Ferramenta de Criação de Imagens (ISO)
"""

import subprocess
import shutil
import tempfile
import os
from pathlib import Path
from typing import Optional
from logger import get_logger

logger = get_logger()

class DistroBuilder:
    """Constrói uma imagem ISO do ProteusOS a partir de snapshots."""

    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.snapshots_dir = self.base_dir / "snapshots"
        self.logger = get_logger()

    def build_iso(self, snapshot_id: str, kernel_path: Optional[Path] = None,
                  output_name: str = "proteusos.iso") -> bool:
        """
        Constrói uma imagem ISO bootável a partir de um snapshot e um kernel.
        """
        snapshot_path = self.snapshots_dir / f"{snapshot_id}.tar.gz"
        if not snapshot_path.exists():
            self.logger.error(f"Snapshot não encontrado: {snapshot_path}")
            return False

        if not kernel_path or not kernel_path.exists():
            self.logger.error(f"Kernel não encontrado: {kernel_path}")
            return False

        if not shutil.which("xorriso"):
            self.logger.error("xorriso não está instalado. Instale com: sudo apt install xorriso")
            return False

        with tempfile.TemporaryDirectory(prefix="proteus-iso-") as temp_dir:
            temp_dir = Path(temp_dir)
            rootfs_dir = temp_dir / "rootfs"
            iso_dir = temp_dir / "iso"

            rootfs_dir.mkdir(parents=True, exist_ok=True)
            iso_dir.mkdir(parents=True, exist_ok=True)

            self.logger.info(f"Extraindo snapshot {snapshot_id} para {rootfs_dir}...")
            try:
                subprocess.run(
                    ["sudo", "tar", "-xzf", str(snapshot_path), "-C", str(rootfs_dir)],
                    check=True,
                    capture_output=True
                )
                subprocess.run(
                    ["sudo", "chown", "-R", f"{os.getuid()}:{os.getgid()}", str(rootfs_dir)],
                    check=True
                )
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Erro ao extrair snapshot: {e.stderr.decode()}")
                return False

            if not any(rootfs_dir.iterdir()):
                self.logger.error(f"Snapshot extraído está vazio: {rootfs_dir}")
                return False

            # Copia o kernel para o diretório de boot
            boot_dir = iso_dir / "boot"
            boot_dir.mkdir(parents=True, exist_ok=True)

            try:
                shutil.copy2(kernel_path, boot_dir / "vmlinuz")
            except PermissionError:
                try:
                    subprocess.run([
                        "sudo", "cp", str(kernel_path), str(boot_dir / "vmlinuz")
                    ], check=True)
                    subprocess.run([
                        "sudo", "chown", f"{os.getuid()}:{os.getgid()}", str(boot_dir / "vmlinuz")
                    ], check=True)
                except subprocess.CalledProcessError as e:
                    self.logger.error(f"Erro ao copiar kernel com sudo: {e}")
                    return False

            self.logger.info(f"Kernel copiado para {boot_dir / 'vmlinuz'}")

            # Cria o initrd
            initrd_path = self._create_initrd(rootfs_dir)
            if initrd_path:
                shutil.copy2(initrd_path, boot_dir / "initrd.img")
                self.logger.info(f"Initrd criado em {boot_dir / 'initrd.img'}")
            else:
                self.logger.warning("Initrd não criado, continuando sem ele")

            # Cria o arquivo de configuração do GRUB
            grub_dir = iso_dir / "boot/grub"
            grub_dir.mkdir(parents=True, exist_ok=True)

            grub_cfg = grub_dir / "grub.cfg"
            grub_cfg.write_text("""
set timeout=5
set default=0

menuentry "ProteusOS" {
    linux /boot/vmlinuz root=/dev/ram0 init=/init
    initrd /boot/initrd.img
}
""")
            self.logger.info(f"GRUB config criado em {grub_cfg}")

            # Gera a ISO bootável usando xorriso com as opções corretas
            output_path = Path(output_name).absolute()
            self.logger.info(f"Gerando ISO bootável em {output_path}...")

            # Constrói o comando xorriso com as opções para boot
            cmd = [
                "xorriso", "-as", "mkisofs",
                "-r",  # Rock Ridge (para preservar permissões)
                "-J",  # Joliet (para compatibilidade com Windows)
                "-joliet-long",
                "-cache-inodes",
                "-iso-level", "3",
                "-full-iso9660-filenames",
                "-volid", "PROTEUSOS",
                "-eltorito-boot", "boot/grub/grub.cfg",  # Ponto de entrada do GRUB
                "-no-emul-boot",
                "-boot-load-size", "4",
                "-boot-info-table",
                "-eltorito-catalog", "boot.catalog",
                "-output", str(output_path),
                str(iso_dir)
            ]

            try:
                subprocess.run(cmd, check=True, capture_output=True)
                self.logger.info(f"ISO bootável gerada com sucesso: {output_path}")
                print(f"✅ ISO bootável gerada com sucesso: {output_path}")
                print(f"   Tamanho: {output_path.stat().st_size / (1024*1024):.2f} MB")
                print(f"   Use: qemu-system-x86_64 -cdrom {output_path} -m 512")
                print(f"   Ou grave em um pendrive: sudo dd if={output_path} of=/dev/sdX bs=4M status=progress")
                return True
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Erro ao gerar ISO: {e.stderr.decode()}")
                return False

    def _create_initrd(self, rootfs_dir: Path) -> Optional[Path]:
        """Cria um initrd a partir do rootfs."""
        initrd_dir = rootfs_dir / "initrd"
        initrd_dir.mkdir(parents=True, exist_ok=True)

        init_script = initrd_dir / "init"
        init_script.write_text("""#!/bin/sh
echo "ProteusOS - Iniciando..."
mount -t proc none /proc
mount -t sysfs none /sys
echo "Montando sistema de arquivos raiz..."
exec /sbin/init
""")
        init_script.chmod(0o755)

        initrd_path = rootfs_dir / "initrd.img"
        try:
            cmd = f"cd {initrd_dir} && find . -print0 | cpio --null -o --format=newc > {initrd_path}"
            subprocess.run(cmd, shell=True, check=True, executable="/bin/bash")
            return initrd_path
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Erro ao criar initrd: {e}")
            return None
