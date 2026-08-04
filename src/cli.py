#!/usr/bin/env python3
"""
Interface de Linha de Comando do ProteusOS
Gerencia as operações de build, update e rollback
"""

import sys
import os
import argparse
import json
from pathlib import Path
from typing import Optional

# Adiciona o diretório atual ao path para importar os módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from builder import SystemBuilder
from pkg_manager import PackageManager
from updater import SystemUpdater

class ProteusCLI:
    """
    CLI principal do ProteusOS
    """
    
    def __init__(self, base_dir: str = "~/proteus_os"):
        """
        Inicializa a CLI
        
        Args:
            base_dir: Diretório base do ProteusOS
        """
        self.base_dir = os.path.expanduser(base_dir)
        self.builder = SystemBuilder(base_dir)
        self.pkg_manager = PackageManager(base_dir)
        self.updater = SystemUpdater(base_dir)
    
    def cmd_build(self, args):
        """
        Comando: build
        Constrói uma nova imagem/snapshot do sistema
        """
        base_image = args.base_image or "alpine"
        print(f"[ProteusOS] Construindo sistema base: {base_image}")
        
        try:
            snapshot_id = self.builder.build_system(base_image)
            print(f"[ProteusOS] Build concluído com sucesso!")
            print(f"[ProteusOS] Snapshot: {snapshot_id}")
            
            if args.verbose:
                info = self.builder.get_snapshot_info(snapshot_id)
                print(f"\nDetalhes do snapshot:")
                print(json.dumps(info, indent=2))
            
            return 0
        except Exception as e:
            print(f"[ProteusOS] Erro durante build: {e}", file=sys.stderr)
            return 1
    
    def cmd_update(self, args):
        """
        Comando: update
        Aplica uma atualização de forma atômica
        """
        update_path = args.update_path
        
        if not os.path.exists(update_path):
            print(f"[ProteusOS] Atualização não encontrada: {update_path}", file=sys.stderr)
            return 1
        
        print(f"[ProteusOS] Aplicando atualização: {update_path}")
        
        try:
            success, message = self.updater.apply_update(update_path)
            
            if success:
                print(f"[ProteusOS] {message}")
                
                if args.verbose:
                    updates = self.updater.list_updates()
                    if updates:
                        last_update = updates[-1]
                        print(f"\nDetalhes da atualização:")
                        print(json.dumps(last_update, indent=2))
                return 0
            else:
                print(f"[ProteusOS] Falha: {message}", file=sys.stderr)
                return 1
        except Exception as e:
            print(f"[ProteusOS] Erro durante atualização: {e}", file=sys.stderr)
            return 1
    
    def cmd_rollback(self, args):
        """
        Comando: rollback
        Reverte para o snapshot estável anterior
        """
        print("[ProteusOS] Realizando rollback...")
        
        try:
            target_snapshot = args.snapshot_id
            success, message = self.updater.rollback_update(target_snapshot)
            
            if success:
                print(f"[ProteusOS] {message}")
                if args.verbose:
                    current = self.builder.get_current_snapshot()
                    print(f"[ProteusOS] Snapshot atual: {current}")
                return 0
            else:
                print(f"[ProteusOS] Falha no rollback: {message}", file=sys.stderr)
                return 1
        except Exception as e:
            print(f"[ProteusOS] Erro durante rollback: {e}", file=sys.stderr)
            return 1
    
    def cmd_status(self, args):
        """
        Comando: status
        Mostra o snapshot atual e os disponíveis
        """
        print("[ProteusOS] Status do sistema")
        print("-" * 50)
        
        try:
            # Snapshot atual
            current = self.builder.get_current_snapshot()
            print(f"Snapshot atual: {current or 'Nenhum'}")
            
            if current:
                info = self.builder.get_snapshot_info(current)
                if info:
                    print(f"  Criado em: {info.get('created_at', 'N/A')}")
                    print(f"  Tamanho: {info.get('size', 0) / 1024 / 1024:.2f} MB")
            
            # Snapshots disponíveis
            snapshots = self.builder.list_snapshots()
            print(f"\nSnapshots disponíveis: {len(snapshots)}")
            for snapshot in snapshots:
                info = self.builder.get_snapshot_info(snapshot)
                marker = "-> " if snapshot == current else "   "
                print(f"  {marker}{snapshot}")
            
            # Atualizações aplicadas
            updates = self.updater.list_updates()
            print(f"\nAtualizações aplicadas: {len(updates)}")
            for update in updates[-5:]:  # Mostra as últimas 5
                print(f"  - {update.get('id', 'N/A')} em {update.get('applied_at', 'N/A')}")
            
            # Pacotes instalados
            packages = self.pkg_manager.list_packages()
            print(f"\nPacotes instalados: {len(packages)}")
            for package in packages:
                print(f"  - {package.get('name', 'N/A')} ({package.get('id', 'N/A')})")
            
            return 0
        except Exception as e:
            print(f"[ProteusOS] Erro ao obter status: {e}", file=sys.stderr)
            return 1
    
    def cmd_package(self, args):
        """
        Comando: package
        Gerencia pacotes
        """
        if args.package_action == "install":
            return self._cmd_install_package(args)
        elif args.package_action == "uninstall":
            return self._cmd_uninstall_package(args)
        elif args.package_action == "list":
            return self._cmd_list_packages(args)
        else:
            print(f"[ProteusOS] Ação desconhecida: {args.package_action}", file=sys.stderr)
            return 1
    
    def _cmd_install_package(self, args):
        """Instala um pacote"""
        print(f"[ProteusOS] Instalando pacote: {args.package_path}")
        
        try:
            success, message = self.pkg_manager.install_package(args.package_path)
            if success:
                print(f"[ProteusOS] {message}")
                return 0
            else:
                print(f"[ProteusOS] Falha: {message}", file=sys.stderr)
                return 1
        except Exception as e:
            print(f"[ProteusOS] Erro ao instalar pacote: {e}", file=sys.stderr)
            return 1
    
    def _cmd_uninstall_package(self, args):
        """Desinstala um pacote"""
        print(f"[ProteusOS] Desinstalando pacote: {args.package_id}")
        
        try:
            success, message = self.pkg_manager.uninstall_package(args.package_id)
            if success:
                print(f"[ProteusOS] {message}")
                return 0
            else:
                print(f"[ProteusOS] Falha: {message}", file=sys.stderr)
                return 1
        except Exception as e:
            print(f"[ProteusOS] Erro ao desinstalar pacote: {e}", file=sys.stderr)
            return 1
    
    def _cmd_list_packages(self, args):
        """Lista pacotes instalados"""
        try:
            packages = self.pkg_manager.list_packages()
            print(f"[ProteusOS] Pacotes instalados: {len(packages)}")
            
            if args.verbose:
                for package in packages:
                    print(json.dumps(package, indent=2))
            else:
                for package in packages:
                    print(f"  - {package.get('name', 'N/A')} ({package.get('id', 'N/A')})")
            
            return 0
        except Exception as e:
            print(f"[ProteusOS] Erro ao listar pacotes: {e}", file=sys.stderr)
            return 1

def main():
    """Ponto de entrada principal do CLI"""
    parser = argparse.ArgumentParser(
        description="ProteusOS - Sistema Operacional Minimalista e Modular",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  proteus build --base-image alpine
  proteus update /path/to/update
  proteus rollback
  proteus status
  proteus package install /path/to/package
  proteus package list
        """
    )
    
    parser.add_argument(
        "--base-dir",
        default="~/proteus_os",
        help="Diretório base do ProteusOS (padrão: ~/proteus_os)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Saída detalhada"
    )
    
    subparsers = parser.add_subparsers(
        dest="command",
        help="Comandos disponíveis",
        required=True
    )
    
    # Comando: build
    build_parser = subparsers.add_parser(
        "build",
        help="Constrói uma nova imagem/snapshot do sistema"
    )
    build_parser.add_argument(
        "--base-image",
        choices=["alpine", "debian"],
        default="alpine",
        help="Imagem base a ser usada (padrão: alpine)"
    )
    build_parser.add_argument(
        "--freeze",
        action="store_true",
        help="Congela o estado atual após o build"
    )
    
    # Comando: update
    update_parser = subparsers.add_parser(
        "update",
        help="Aplica uma atualização de forma atômica"
    )
    update_parser.add_argument(
        "update_path",
        help="Caminho para o pacote de atualização"
    )
    
    # Comando: rollback
    rollback_parser = subparsers.add_parser(
        "rollback",
        help="Reverte para o snapshot estável anterior"
    )
    rollback_parser.add_argument(
        "--snapshot-id",
        help="ID do snapshot específico para rollback"
    )
    
    # Comando: status
    status_parser = subparsers.add_parser(
        "status",
        help="Mostra o snapshot atual e os disponíveis"
    )
    
    # Comando: package
    package_parser = subparsers.add_parser(
        "package",
        help="Gerencia pacotes do sistema"
    )
    package_subparsers = package_parser.add_subparsers(
        dest="package_action",
        help="Ações para gerenciamento de pacotes",
        required=True
    )
    
    # Subcomandos de package
    install_pkg = package_subparsers.add_parser(
        "install",
        help="Instala um pacote"
    )
    install_pkg.add_argument(
        "package_path",
        help="Caminho para o pacote"
    )
    
    uninstall_pkg = package_subparsers.add_parser(
        "uninstall",
        help="Desinstala um pacote"
    )
    uninstall_pkg.add_argument(
        "package_id",
        help="ID do pacote a ser desinstalado"
    )
    
    list_pkg = package_subparsers.add_parser(
        "list",
        help="Lista pacotes instalados"
    )
    
    # Parse dos argumentos
    args = parser.parse_args()
    
    # Inicializa a CLI
    cli = ProteusCLI(args.base_dir)
    
    # Executa o comando
    if args.command == "build":
        return cli.cmd_build(args)
    elif args.command == "update":
        return cli.cmd_update(args)
    elif args.command == "rollback":
        return cli.cmd_rollback(args)
    elif args.command == "status":
        return cli.cmd_status(args)
    elif args.command == "package":
        return cli.cmd_package(args)
    else:
        print(f"Comando desconhecido: {args.command}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())