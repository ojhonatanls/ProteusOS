#!/usr/bin/env python3
"""
ProteusOS - Image Builder (ISO)
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
    """Builds a bootable ISO image of ProteusOS from snapshots."""

    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.snapshots_dir = self.base_dir / "snapshots"
        self.logger = get_logger()

    def _check_tools(self):
        """Checks if the necessary tools are installed."""
        required_tools = {
            'xorriso': 'sudo apt install xorriso',
            'grub-mkrescue': 'sudo apt install grub-pc-bin grub-common',
            'cpio': 'sudo apt install cpio'
        }
        missing = []
        for tool, install_cmd in required_tools.items():
            if not shutil.which(tool):
                missing.append(f"{tool} (install with: {install_cmd})")
        if missing:
            from exceptions import ToolNotFoundError
            raise ToolNotFoundError(f"Missing tools: {', '.join(missing)}")

    def build_iso(self, snapshot_id: str, kernel_path: Optional[Path] = None,
                  output_name: str = "proteusos.iso") -> bool:
        """
        Builds a bootable ISO image from a snapshot and a kernel.
        """
        self._check_tools()

        snapshot_path = self.snapshots_dir / f"{snapshot_id}.tar.gz"
        if not snapshot_path.exists():
            self.logger.error(f"Snapshot not found: {snapshot_path}")
            return False

        if not kernel_path or not kernel_path.exists():
            self.logger.error(f"Kernel not found: {kernel_path}")
            return False

        if not shutil.which("xorriso"):
            self.logger.error("xorriso is not installed. Install with: sudo apt install xorriso")
            return False

        with tempfile.TemporaryDirectory(prefix="proteus-iso-") as temp_dir:
            temp_dir = Path(temp_dir)
            rootfs_dir = temp_dir / "rootfs"
            iso_dir = temp_dir / "iso"

            rootfs_dir.mkdir(parents=True, exist_ok=True)
            iso_dir.mkdir(parents=True, exist_ok=True)

            self.logger.info(f"Extracting snapshot {snapshot_id} to {rootfs_dir}...")
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
                self.logger.error(f"Error extracting snapshot: {e.stderr.decode()}")
                return False

            if not any(rootfs_dir.iterdir()):
                self.logger.error(f"Extracted snapshot is empty: {rootfs_dir}")
                return False

            boot_dir = iso_dir / "boot"
            boot_dir.mkdir(parents=True, exist_ok=True)

            try:
                shutil.copy2(kernel_path, boot_dir / "vmlinuz")
            except PermissionError:
                self.logger.warning("Permission denied copying kernel. Trying with sudo...")
                try:
                    subprocess.run([
                        "sudo", "cp", str(kernel_path), str(boot_dir / "vmlinuz")
                    ], check=True)
                    subprocess.run([
                        "sudo", "chown", f"{os.getuid()}:{os.getgid()}", str(boot_dir / "vmlinuz")
                    ], check=True)
                except subprocess.CalledProcessError as e:
                    self.logger.error(f"Error copying kernel with sudo: {e}")
                    return False

            self.logger.info(f"Kernel copied to {boot_dir / 'vmlinuz'}")

            initrd_path = self._create_initrd(rootfs_dir)
            if initrd_path:
                shutil.copy2(initrd_path, boot_dir / "initrd.img")
                self.logger.info(f"Initrd created at {boot_dir / 'initrd.img'}")
            else:
                self.logger.warning("Initrd not created, continuing without it")

            grub_dir = iso_dir / "boot/grub"
            grub_dir.mkdir(parents=True, exist_ok=True)

            grub_cfg = grub_dir / "grub.cfg"
            grub_cfg.write_text("""
set timeout=5
set default=0

menuentry "ProteusOS" {
    linux /boot/vmlinuz root=/dev/ram0
    initrd /boot/initrd.img
}
""")
            self.logger.info(f"GRUB config created at {grub_cfg}")

            output_path = Path(output_name).absolute()
            self.logger.info(f"Generating ISO at {output_path}...")

            cmd = [
                "xorriso", "-as", "mkisofs",
                "-r",
                "-J",
                "-joliet-long",
                "-cache-inodes",
                "-iso-level", "3",
                "-full-iso9660-filenames",
                "-volid", "PROTEUSOS",
                "-eltorito-boot", "boot/grub/grub.cfg",
                "-no-emul-boot",
                "-boot-load-size", "4",
                "-boot-info-table",
                "-eltorito-catalog", "boot.catalog",
                "-output", str(output_path),
                str(iso_dir)
            ]

            try:
                subprocess.run(cmd, check=True, capture_output=True)
                self.logger.info(f"Bootable ISO generated successfully: {output_path}")
                print(f"ISO generated successfully: {output_path}")
                print(f"   Size: {output_path.stat().st_size / (1024*1024):.2f} MB")
                print(f"   Use: qemu-system-x86_64 -cdrom {output_path} -m 512")
                print(f"   Or write to USB: sudo dd if={output_path} of=/dev/sdX bs=4M status=progress")
                return True
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Error generating ISO: {e.stderr.decode()}")
                return False

    def _create_initrd(self, rootfs_dir: Path) -> Optional[Path]:
        """Creates a basic initrd from the rootfs."""
        initrd_dir = rootfs_dir / "initrd"
        initrd_dir.mkdir(parents=True, exist_ok=True)

        init_script = initrd_dir / "init"
        init_script.write_text("""#!/bin/sh
echo "ProteusOS - Starting..."
mount -t proc none /proc
mount -t sysfs none /sys
echo "Mounting root filesystem..."
exec /sbin/init
""")
        init_script.chmod(0o755)

        initrd_path = rootfs_dir / "initrd.img"
        try:
            cmd = f"cd {initrd_dir} && find . -print0 | cpio --null -o --format=newc > {initrd_path}"
            subprocess.run(cmd, shell=True, check=True, executable="/bin/bash")
            return initrd_path
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error creating initrd: {e}")
            return None
