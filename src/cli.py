#!/usr/bin/env python3
"""
ProteusOS - CLI (Interface de Linha de Comando)
Gerencia os comandos do usuário e orquestra as ações.
"""

import argparse
import sys
import os
import shutil
import subprocess
from pathlib import Path

# Adiciona o diretório src ao path para importar os módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from builder import SystemBuilder
from pkg_manager import PackageManager
from updater import SystemUpdater
from config import Config
from logger import setup_logging, get_logger
from drivers import PackageOrchestrator

# Configura logging
setup_logging()
logger = get_logger()

# Tenta importar o módulo C (se disponível)
try:
    import snapshot
    C_AVAILABLE = True
    logger.debug("C module loaded successfully")
except ImportError:
    C_AVAILABLE = False
    logger.debug("C module not available, using pure Python")

class ProteusCLI:
    def __init__(self):
        self.config = Config()
        self.base_dir = Path(self.config.get("base_dir", str(Path.home() / "proteus_os")))
        self.builder = SystemBuilder(self.base_dir)
        self.pkg_manager = PackageManager(self.base_dir)
        self.updater = SystemUpdater(self.base_dir)
        self.export_dir = Path.home() / "proteus_exports"
        self.export_dir.mkdir(exist_ok=True)
        self.orchestrator = PackageOrchestrator()
        logger.info(f"ProteusOS initialized. Base dir: {self.base_dir}")

    def run(self, args=None):
        parser = argparse.ArgumentParser(
            description="ProteusOS - Minimalist and Modular Operating System",
            epilog="Use 'proteus <command> --help' for more details."
        )
        subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

        # Comando: build
        parser_build = subparsers.add_parser("build", help="Build a base system")
        parser_build.add_argument("--base-image", required=True, choices=["alpine", "debian"], help="Base image")
        parser_build.add_argument("--use-c", action="store_true", help="Use C implementation (experimental)")
        parser_build.add_argument("--full", action="store_true", help="Create full snapshot (not diff)")

        # Comando: status
        parser_status = subparsers.add_parser("status", help="System status and snapshots")

        # Comando: update
        parser_update = subparsers.add_parser("update", help="Apply an update")
        parser_update.add_argument("update_path", help="Path to update package")

        # Comando: rollback
        parser_rollback = subparsers.add_parser("rollback", help="Rollback to a snapshot")
        parser_rollback.add_argument("--snapshot-id", help="Specific snapshot ID")

        # Comando: package (nativo do ProteusOS)
        parser_pkg = subparsers.add_parser("package", help="Manage packages (native)")
        subparsers_pkg = parser_pkg.add_subparsers(dest="pkg_command", required=True, help="Package actions")
        parser_pkg_install = subparsers_pkg.add_parser("install", help="Install a package")
        parser_pkg_install.add_argument("package_path", help="Path to package")
        parser_pkg_list = subparsers_pkg.add_parser("list", help="List installed packages")
        parser_pkg_uninstall = subparsers_pkg.add_parser("uninstall", help="Uninstall a package")
        parser_pkg_uninstall.add_argument("package_id", help="Package ID")

        # Comando: pts (gerenciador de pacotes universal)
        parser_pts = subparsers.add_parser("pts", help="Universal package manager (APT + DNF + Pacman)")
        parser_pts.add_argument("action", choices=["install", "remove", "list", "search"], help="Action to perform")
        parser_pts.add_argument("package", nargs="?", help="Package name (for install/remove/search)")
        parser_pts.add_argument("--driver", choices=["apt", "dnf", "pacman"], help="Force a specific driver")

        # Comando: config
        parser_config = subparsers.add_parser("config", help="Manage configurations")
        parser_config.add_argument("--show", action="store_true", help="Show current configurations")
        parser_config.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"), help="Set a configuration")

        # Comando: info
        parser_info = subparsers.add_parser("info", help="Detailed snapshot or package information")
        parser_info.add_argument("target", help="Snapshot or package ID")

        # Comando: export
        parser_export = subparsers.add_parser("export", help="Export a snapshot to .tar.gz")
        parser_export.add_argument("snapshot_id", help="Snapshot ID to export")
        parser_export.add_argument("--output", "-o", help="Output file path")

        # Comando: import
        parser_import = subparsers.add_parser("import", help="Import a snapshot from .tar.gz")
        parser_import.add_argument("file_path", help="Path to .tar.gz file")

        # Comando: cleanup
        parser_cleanup = subparsers.add_parser("cleanup", help="Remove old snapshots")
        parser_cleanup.add_argument("--keep", type=int, default=5, help="Number of recent snapshots to keep")
        parser_cleanup.add_argument("--snapshot-id", help="Remove a specific snapshot")

        # Comando: service
        parser_service = subparsers.add_parser("service", help="Manage system services")
        parser_service.add_argument("action", choices=["enable", "disable", "start", "stop", "list"], help="Action to perform")
        parser_service.add_argument("service_name", nargs="?", help="Service name")

        # Comando: distro-build
        parser_distro = subparsers.add_parser("distro-build", help="Build a bootable ISO image")
        parser_distro.add_argument("--snapshot-id", required=True, help="Base snapshot ID")
        parser_distro.add_argument("--kernel", required=True, help="Path to kernel (vmlinuz)")
        parser_distro.add_argument("--output", "-o", default="proteusos.iso", help="Output ISO filename")

        parsed_args = parser.parse_args(args)

        try:
            if parsed_args.command == "build":
                self._cmd_build(parsed_args)
            elif parsed_args.command == "status":
                self._cmd_status()
            elif parsed_args.command == "update":
                self._cmd_update(parsed_args)
            elif parsed_args.command == "rollback":
                self._cmd_rollback(parsed_args)
            elif parsed_args.command == "package":
                self._cmd_package(parsed_args)
            elif parsed_args.command == "pts":
                self._cmd_pts(parsed_args)
            elif parsed_args.command == "config":
                self._cmd_config(parsed_args)
            elif parsed_args.command == "info":
                self._cmd_info(parsed_args)
            elif parsed_args.command == "export":
                self._cmd_export(parsed_args)
            elif parsed_args.command == "import":
                self._cmd_import(parsed_args)
            elif parsed_args.command == "cleanup":
                self._cmd_cleanup(parsed_args)
            elif parsed_args.command == "service":
                self._cmd_service(parsed_args)
            elif parsed_args.command == "distro-build":
                self._cmd_distro_build(parsed_args)
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"Error: {e}")
            sys.exit(1)

    def _cmd_build(self, args):
        print(f"Building system base: {args.base_image}...")
        logger.info(f"Build started: {args.base_image}")

        if C_AVAILABLE and args.use_c:
            try:
                snapshot_id = snapshot.build(args.base_image)
                print(f"System built successfully (C)! Snapshot: {snapshot_id}")
                logger.info(f"Build completed (C): {snapshot_id}")
                return
            except Exception as e:
                logger.error(f"C module error: {e}")
                print(f"Warning: C module error: {e}")
                print("   Using Python implementation...")

        snapshot_id = self.builder.build_base(args.base_image, full=args.full)
        print(f"System built successfully! Snapshot: {snapshot_id}")
        logger.info(f"Build completed: {snapshot_id}")

    def _cmd_status(self):
        status = self.builder.get_status()
        current = self.builder.get_current_snapshot()
        metadata = self.builder._load_metadata()
        print("ProteusOS System Status")
        print(f"   Base Directory: {self.base_dir}")
        print(f"   Current Snapshot: {current or 'None'}")
        print(f"   Available Snapshots:")
        if not status:
            print("     (No snapshots found)")
        for snap in status:
            info = next((s for s in metadata["snapshots"] if s["id"] == snap), {})
            full_marker = " (full)" if info.get("full", True) else " (diff)"
            marker = " ▶" if snap == current else ""
            print(f"     - {snap}{full_marker}{marker}")
        logger.debug(f"Status: {len(status)} snapshots, current: {current}")

    def _cmd_update(self, args):
        print(f"Applying update from: {args.update_path}...")
        logger.info(f"Update started: {args.update_path}")
        try:
            result = self.updater.apply_update(args.update_path)
            print(f"Update applied: {result}")
            logger.info(f"Update completed: {result}")
        except Exception as e:
            logger.error(f"Update error: {e}")
            raise

    def _cmd_rollback(self, args):
        if args.snapshot_id:
            print(f"Rolling back to: {args.snapshot_id}...")
            logger.info(f"Rollback initiated: {args.snapshot_id}")
            result = self.updater.rollback(args.snapshot_id)
        else:
            print("Rolling back to last stable snapshot...")
            logger.info("Rollback to last stable snapshot")
            result = self.updater.rollback()
        print(f"Rollback completed: {result}")
        logger.info(f"Rollback completed: {result}")

    def _cmd_package(self, args):
        if args.pkg_command == "install":
            print(f"Installing package: {args.package_path}...")
            logger.info(f"Package installation: {args.package_path}")
            pkg_id = self.pkg_manager.install(args.package_path)
            print(f"Package installed successfully! ID: {pkg_id}")
            logger.info(f"Package installed: {pkg_id}")
        elif args.pkg_command == "list":
            print("Installed packages:")
            packages = self.pkg_manager.list_packages()
            if not packages:
                print("   (No packages installed)")
            for pkg in packages:
                print(f"   - {pkg}")
        elif args.pkg_command == "uninstall":
            print(f"Uninstalling package: {args.package_id}...")
            logger.info(f"Package uninstall: {args.package_id}")
            result = self.pkg_manager.uninstall(args.package_id)
            print(f"Package uninstalled: {result}")
            logger.info(f"Package uninstalled: {result}")

    def _cmd_pts(self, args):
        """Executa o gerenciador de pacotes universal (APT + DNF + Pacman)."""
        if args.action == "install":
            if not args.package:
                print("Please specify a package to install")
                logger.error("pts install command without package")
                return
            print(f"Installing {args.package} via universal package manager...")
            success = self.orchestrator.install(args.package, args.driver)
            if success:
                print(f"Package {args.package} installed successfully!")
            else:
                print(f"Failed to install {args.package}")

        elif args.action == "remove":
            if not args.package:
                print("Please specify a package to remove")
                logger.error("pts remove command without package")
                return
            print(f"Removing {args.package}...")
            success = self.orchestrator.remove(args.package, args.driver)
            if success:
                print(f"Package {args.package} removed successfully!")
            else:
                print(f"Failed to remove {args.package}")

        elif args.action == "list":
            print("Installed packages (via universal package manager):")
            packages = self.orchestrator.list_installed(args.driver)
            if not packages:
                print("   (No packages found)")
            for pkg in packages[:20]:
                print(f"   - {pkg}")
            if len(packages) > 20:
                print(f"   ... and {len(packages) - 20} more packages")

        elif args.action == "search":
            if not args.package:
                print("Please specify a search term")
                logger.error("pts search command without term")
                return
            print(f"Searching for: {args.package}")
            results = self.orchestrator.search(args.package, args.driver)
            if not results:
                print("   (No results found)")
            for result in results[:20]:
                print(f"   {result}")
            if len(results) > 20:
                print(f"   ... and {len(results) - 20} more results")

    def _cmd_config(self, args):
        if args.show:
            self.config.show()
        elif args.set:
            key, value = args.set
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            elif value.isdigit():
                value = int(value)
            self.config.set(key, value)
            print(f"Configuration set: {key} = {value}")
            logger.info(f"Configuration set: {key} = {value}")
        else:
            print("Usage: config --show or config --set KEY VALUE")

    def _cmd_info(self, args):
        target = args.target
        snapshots = self.builder.get_status()
        if target in snapshots:
            metadata = self.builder._load_metadata()
            for snap in metadata["snapshots"]:
                if snap["id"] == target:
                    print(f"Snapshot: {target}")
                    print(f"   Base Image: {snap.get('base_image', 'N/A')}")
                    print(f"   Created: {snap.get('timestamp', 'N/A')}")
                    print(f"   Checksum: {snap.get('checksum', 'N/A')[:16]}...")
                    print(f"   Type: {'Full' if snap.get('full', True) else 'Diff'}")
                    parent = snap.get('parent')
                    if parent:
                        print(f"   Base: {parent}")
                    print(f"   Status: {'Active ▶' if target == metadata.get('current') else 'Archived'}")
                    return
        installed = self.pkg_manager._load_installed()
        for pkg in installed["packages"]:
            if pkg["id"] == target:
                print(f"Package: {pkg.get('name', 'N/A')}")
                print(f"   Version: {pkg.get('version', 'N/A')}")
                print(f"   ID: {pkg['id']}")
                print(f"   Installed: {pkg.get('timestamp', 'N/A')}")
                deps = pkg.get("dependencies", {})
                if deps:
                    print(f"   Dependencies: {', '.join([f'{k}=={v}' for k, v in deps.items()])}")
                else:
                    print("   Dependencies: None")
                return
        print(f"No snapshot or package found with ID: {target}")

    def _cmd_export(self, args):
        snapshot_id = args.snapshot_id
        snapshot_path = self.builder.snapshots_dir / f"{snapshot_id}.tar.gz"

        if not snapshot_path.exists():
            print(f"Snapshot '{snapshot_id}' not found")
            return

        if args.output:
            output_path = Path(args.output)
        else:
            output_path = self.export_dir / f"{snapshot_id}.tar.gz"

        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            shutil.copy2(snapshot_path, output_path)
            print(f"Snapshot '{snapshot_id}' exported successfully to:")
            print(f"   {output_path}")
            size = output_path.stat().st_size / (1024*1024)
            print(f"   Size: {size:.2f} MB")
            logger.info(f"Snapshot exported: {snapshot_id} -> {output_path}")
        except Exception as e:
            logger.error(f"Export error: {e}")
            print(f"Error exporting snapshot: {e}")

    def _cmd_import(self, args):
        file_path = Path(args.file_path)

        if not file_path.exists():
            print(f"File not found: {file_path}")
            return

        if not file_path.suffix == '.gz' or not file_path.name.endswith('.tar.gz'):
            print("The file must be a valid .tar.gz")
            return

        snapshot_id = file_path.stem.replace('.tar', '')

        if self.builder.snapshot_exists(snapshot_id):
            print(f"Snapshot '{snapshot_id}' already exists locally.")
            resposta = input("   Overwrite? (y/N): ")
            if resposta.lower() != 'y':
                print("Import cancelled.")
                return

        destino = self.builder.snapshots_dir / f"{snapshot_id}.tar.gz"
        try:
            shutil.copy2(file_path, destino)
            print(f"Snapshot '{snapshot_id}' imported successfully!")

            metadata = self.builder._load_metadata()
            if not any(s['id'] == snapshot_id for s in metadata["snapshots"]):
                base_image = "unknown"
                if "_alpine" in snapshot_id:
                    base_image = "alpine"
                elif "_debian" in snapshot_id:
                    base_image = "debian"
                elif "_updated" in snapshot_id:
                    base_image = "updated"

                metadata["snapshots"].append({
                    "id": snapshot_id,
                    "base_image": base_image,
                    "timestamp": "imported",
                    "full": True
                })
                self.builder._save_metadata(metadata)
                print("Metadata updated for imported snapshot.")
            else:
                print("Metadata already exists for this snapshot.")
            logger.info(f"Snapshot imported: {snapshot_id}")
        except Exception as e:
            logger.error(f"Import error: {e}")
            print(f"Error importing snapshot: {e}")

    def _cmd_cleanup(self, args):
        if args.snapshot_id:
            snapshot_path = self.builder.snapshots_dir / f"{args.snapshot_id}.tar.gz"
            if not snapshot_path.exists():
                print(f"Snapshot '{args.snapshot_id}' not found")
                return

            if self.builder.get_current_snapshot() == args.snapshot_id:
                print("Cannot remove the current snapshot.")
                return

            resposta = input(f"Remove snapshot '{args.snapshot_id}' permanently? (y/N): ")
            if resposta.lower() == 'y':
                snapshot_path.unlink()
                metadata = self.builder._load_metadata()
                metadata["snapshots"] = [s for s in metadata["snapshots"] if s["id"] != args.snapshot_id]
                self.builder._save_metadata(metadata)
                print(f"Snapshot '{args.snapshot_id}' removed successfully!")
                logger.info(f"Snapshot removed: {args.snapshot_id}")
            else:
                print("Operation cancelled.")
            return

        snapshots = self.builder.get_status()
        if len(snapshots) <= args.keep:
            print(f"Only {len(snapshots)} snapshots found. No action needed.")
            return

        def get_timestamp(snap_id):
            try:
                parts = snap_id.split('_')
                if len(parts) >= 3:
                    return parts[1] + parts[2]
            except:
                pass
            return "00000000000000"

        snapshots_ordenados = sorted(snapshots, key=get_timestamp, reverse=True)
        snapshots_para_remover = snapshots_ordenados[args.keep:]

        print(f"Removing {len(snapshots_para_remover)} old snapshot(s)...")
        for snap_id in snapshots_para_remover:
            if self.builder.get_current_snapshot() == snap_id:
                print(f"   Skipping current snapshot: {snap_id}")
                continue

            snapshot_path = self.builder.snapshots_dir / f"{snap_id}.tar.gz"
            if snapshot_path.exists():
                snapshot_path.unlink()
                print(f"   Removed: {snap_id}")
                logger.info(f"Snapshot removed in cleanup: {snap_id}")

        metadata = self.builder._load_metadata()
        current_snapshot = self.builder.get_current_snapshot()
        metadata["snapshots"] = [s for s in metadata["snapshots"] if s["id"] in snapshots_ordenados[:args.keep] or s["id"] == current_snapshot]
        self.builder._save_metadata(metadata)
        print(f"Cleanup complete! Kept {args.keep} recent snapshots.")

    def _cmd_service(self, args):
        from init_manager import InitManager
        manager = InitManager()

        if args.action == "list":
            services = manager.list_services()
            if not services:
                print("No services found.")
                return
            print(f"Active services ({len(services)}):")
            for svc in services[:20]:
                print(f"   - {svc}")
            if len(services) > 20:
                print(f"   ... and {len(services) - 20} more services")

        elif args.action == "enable":
            if not args.service_name:
                print("Please specify a service name")
                return
            if manager.enable_service(args.service_name):
                print(f"Service '{args.service_name}' enabled successfully!")
            else:
                print(f"Failed to enable '{args.service_name}'")

        elif args.action == "disable":
            if not args.service_name:
                print("Please specify a service name")
                return
            if manager.disable_service(args.service_name):
                print(f"Service '{args.service_name}' disabled successfully!")
            else:
                print(f"Failed to disable '{args.service_name}'")

        elif args.action == "start":
            if not args.service_name:
                print("Please specify a service name")
                return
            if manager.start_service(args.service_name):
                print(f"Service '{args.service_name}' started successfully!")
            else:
                print(f"Failed to start '{args.service_name}'")

        elif args.action == "stop":
            if not args.service_name:
                print("Please specify a service name")
                return
            if manager.stop_service(args.service_name):
                print(f"Service '{args.service_name}' stopped successfully!")
            else:
                print(f"Failed to stop '{args.service_name}'")

    def _cmd_distro_build(self, args):
        from distro_builder import DistroBuilder
        builder = DistroBuilder(self.base_dir)
        print("Building ProteusOS ISO...")
        print(f"   Snapshot: {args.snapshot_id}")
        print(f"   Kernel: {args.kernel}")
        print(f"   Output: {args.output}")

        if builder.build_iso(args.snapshot_id, Path(args.kernel), args.output):
            print(f"ISO generated successfully: {args.output}")
            print(f"   Use: sudo dd if={args.output} of=/dev/sdX bs=4M status=progress")
        else:
            print("Failed to generate ISO")
            print("   Make sure xorriso is installed: sudo apt install xorriso")

def main():
    cli = ProteusCLI()
    cli.run()

if __name__ == "__main__":
    main()
