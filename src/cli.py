#!/usr/bin/env python3
"""
ProteusOS - CLI (Interface de Linha de Comando)
Gerencia os comandos do usuário e orquestra as ações.
"""

import argparse
import sys
import os
from pathlib import Path

# Adiciona o diretório src ao path para importar os módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from builder import SystemBuilder
from pkg_manager import PackageManager
from updater import SystemUpdater
from config import Config

class ProteusCLI:
    def __init__(self):
        self.config = Config()
        self.base_dir = Path(self.config.get("base_dir", str(Path.home() / "proteus_os")))
        self.builder = SystemBuilder(self.base_dir)
        self.pkg_manager = PackageManager(self.base_dir)
        self.updater = SystemUpdater(self.base_dir)

    def run(self, args=None):
        parser = argparse.ArgumentParser(
            description="ProteusOS - Sistema Operacional Minimalista e Modular",
            epilog="Use 'proteus <comando> --help' para mais detalhes."
        )
        subparsers = parser.add_subparsers(dest="comando", required=True, help="Comandos disponíveis")

        # Comando: build
        parser_build = subparsers.add_parser("build", help="Construir um sistema base")
        parser_build.add_argument("--base-image", required=True, choices=["alpine", "debian"], help="Imagem base")

        # Comando: status
        parser_status = subparsers.add_parser("status", help="Status do sistema e snapshots")

        # Comando: update
        parser_update = subparsers.add_parser("update", help="Aplicar uma atualização")
        parser_update.add_argument("update_path", help="Caminho para o pacote de atualização")

        # Comando: rollback
        parser_rollback = subparsers.add_parser("rollback", help="Rollback para um snapshot")
        parser_rollback.add_argument("--snapshot-id", help="ID do snapshot específico")

        # Comando: package
        parser_pkg = subparsers.add_parser("package", help="Gerenciar pacotes")
        subparsers_pkg = parser_pkg.add_subparsers(dest="pkg_comando", required=True, help="Ações de pacote")

        # Subcomando: package install
        parser_pkg_install = subparsers_pkg.add_parser("install", help="Instalar um pacote")
        parser_pkg_install.add_argument("package_path", help="Caminho para o pacote")

        # Subcomando: package list
        parser_pkg_list = subparsers_pkg.add_parser("list", help="Listar pacotes instalados")

        # Subcomando: package uninstall
        parser_pkg_uninstall = subparsers_pkg.add_parser("uninstall", help="Desinstalar um pacote")
        parser_pkg_uninstall.add_argument("package_id", help="ID do pacote")

        # Comando: config
        parser_config = subparsers.add_parser("config", help="Gerenciar configurações")
        parser_config.add_argument("--show", action="store_true", help="Mostrar configurações atuais")
        parser_config.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"), help="Definir uma configuração")

        # Comando: info
        parser_info = subparsers.add_parser("info", help="Informações detalhadas de um snapshot ou pacote")
        parser_info.add_argument("target", help="ID do snapshot ou pacote")

        parsed_args = parser.parse_args(args)

        # Executa o comando
        try:
            if parsed_args.comando == "build":
                self._cmd_build(parsed_args)
            elif parsed_args.comando == "status":
                self._cmd_status()
            elif parsed_args.comando == "update":
                self._cmd_update(parsed_args)
            elif parsed_args.comando == "rollback":
                self._cmd_rollback(parsed_args)
            elif parsed_args.comando == "package":
                self._cmd_package(parsed_args)
            elif parsed_args.comando == "config":
                self._cmd_config(parsed_args)
            elif parsed_args.comando == "info":
                self._cmd_info(parsed_args)
        except Exception as e:
            print(f"❌ Erro: {e}")
            sys.exit(1)

    def _cmd_build(self, args):
        print(f"🛠️  Construindo sistema base: {args.base_image}...")
        snapshot_id = self.builder.build_base(args.base_image)
        print(f"✅ Sistema construído com sucesso! Snapshot: {snapshot_id}")

    def _cmd_status(self):
        status = self.builder.get_status()
        current = self.builder.get_current_snapshot()
        print(f"📊 Status do Sistema ProteusOS")
        print(f"   Diretório Base: {self.base_dir}")
        print(f"   Snapshot Atual: {current or 'Nenhum'}")
        print(f"   Snapshots Disponíveis:")
        if not status:
            print("     (Nenhum snapshot encontrado)")
        for snap in status:
            marker = " ▶" if snap == current else ""
            print(f"     - {snap}{marker}")

    def _cmd_update(self, args):
        print(f"🔄 Aplicando atualização de: {args.update_path}...")
        result = self.updater.apply_update(args.update_path)
        print(f"✅ Atualização aplicada: {result}")

    def _cmd_rollback(self, args):
        if args.snapshot_id:
            print(f"⏪ Realizando rollback para: {args.snapshot_id}...")
            result = self.updater.rollback(args.snapshot_id)
        else:
            print(f"⏪ Realizando rollback para o último snapshot estável...")
            result = self.updater.rollback()
        print(f"✅ Rollback concluído: {result}")

    def _cmd_package(self, args):
        if args.pkg_comando == "install":
            print(f"📦 Instalando pacote: {args.package_path}...")
            pkg_id = self.pkg_manager.install(args.package_path)
            print(f"✅ Pacote instalado com sucesso! ID: {pkg_id}")
        elif args.pkg_comando == "list":
            print(f"📦 Pacotes instalados:")
            packages = self.pkg_manager.list_packages()
            if not packages:
                print("   (Nenhum pacote instalado)")
            for pkg in packages:
                print(f"   - {pkg}")
        elif args.pkg_comando == "uninstall":
            print(f"🗑️  Desinstalando pacote: {args.package_id}...")
            result = self.pkg_manager.uninstall(args.package_id)
            print(f"✅ Pacote desinstalado: {result}")

    def _cmd_config(self, args):
        """Gerencia as configurações do sistema."""
        if args.show:
            self.config.show()
        elif args.set:
            key, value = args.set
            # Tenta converter para o tipo apropriado
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            elif value.isdigit():
                value = int(value)
            self.config.set(key, value)
            print(f"✅ Configuração definida: {key} = {value}")
        else:
            print("❌ Uso: config --show ou config --set KEY VALUE")

    def _cmd_info(self, args):
        """Mostra informações detalhadas de um snapshot ou pacote."""
        target = args.target
        
        # Verifica se é um snapshot
        snapshots = self.builder.get_status()
        if target in snapshots:
            metadata = self.builder._load_metadata()
            for snap in metadata["snapshots"]:
                if snap["id"] == target:
                    print(f"📸 Snapshot: {target}")
                    print(f"   Base Image: {snap.get('base_image', 'N/A')}")
                    print(f"   Criado em: {snap.get('timestamp', 'N/A')}")
                    print(f"   Status: {'▶ Ativo' if target == metadata.get('current') else 'Arquivado'}")
                    return
        
        # Verifica se é um pacote
        installed = self.pkg_manager._load_installed()
        for pkg in installed["packages"]:
            if pkg["id"] == target:
                print(f"📦 Pacote: {pkg.get('name', 'N/A')}")
                print(f"   Versão: {pkg.get('version', 'N/A')}")
                print(f"   ID: {pkg['id']}")
                print(f"   Instalado em: {pkg.get('timestamp', 'N/A')}")
                deps = pkg.get("dependencies", {})
                if deps:
                    print(f"   Dependências: {', '.join([f'{k}=={v}' for k, v in deps.items()])}")
                else:
                    print("   Dependências: Nenhuma")
                return
        
        print(f"❌ Nenhum snapshot ou pacote encontrado com ID: {target}")

def main():
    cli = ProteusCLI()
    cli.run()

if __name__ == "__main__":
    main()
