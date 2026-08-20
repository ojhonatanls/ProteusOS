#!/usr/bin/env python3
"""
ProteusOS - Modo Shell Interativo
Permite executar comandos do ProteusOS em um ambiente interativo.
"""

import cmd
import sys
from pathlib import Path

# Adiciona o diretório src ao path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

from cli import ProteusCLI

class ProteusShell(cmd.Cmd):
    intro = """
╔═══════════════════════════════════════════╗
║   🐙 ProteusOS - Modo Shell Interativo   ║
║   Digite 'help' para ver os comandos     ║
║   Digite 'exit' ou 'quit' para sair      ║
╚═══════════════════════════════════════════╝
"""
    prompt = "proteus> "

    def __init__(self):
        super().__init__()
        self.cli = ProteusCLI()

    def do_build(self, arg):
        """Construir um sistema base: build --base-image alpine"""
        if not arg:
            print("❌ Uso: build --base-image alpine|debian")
            return
        self.cli.run(["build"] + arg.split())

    def do_status(self, arg):
        """Ver status do sistema"""
        self.cli.run(["status"])

    def do_update(self, arg):
        """Aplicar uma atualização: update /path/to/update"""
        if not arg:
            print("❌ Uso: update /path/to/update")
            return
        self.cli.run(["update", arg])

    def do_rollback(self, arg):
        """Rollback para um snapshot: rollback [--snapshot-id ID]"""
        if arg:
            self.cli.run(["rollback", "--snapshot-id", arg])
        else:
            self.cli.run(["rollback"])

    def do_package(self, arg):
        """Gerenciar pacotes: package install|list|uninstall [args]"""
        if not arg:
            print("❌ Uso: package install|list|uninstall [args]")
            return
        self.cli.run(["package"] + arg.split())

    def do_clear(self, arg):
        """Limpar a tela"""
        print("\033c", end="")

    def do_exit(self, arg):
        """Sair do shell"""
        print("👋 Saindo do ProteusOS...")
        return True

    def do_quit(self, arg):
        """Sair do shell"""
        return self.do_exit(arg)

    def do_help(self, arg):
        """Mostra ajuda sobre os comandos"""
        if arg:
            super().do_help(arg)
        else:
            print("\n📚 Comandos disponíveis:")
            print("   build    - Construir um sistema base")
            print("   status   - Ver status do sistema")
            print("   update   - Aplicar uma atualização")
            print("   rollback - Rollback para um snapshot")
            print("   package  - Gerenciar pacotes")
            print("   clear    - Limpar a tela")
            print("   exit     - Sair do shell")
            print("   quit     - Sair do shell")
            print("\nDigite 'help <comando>' para mais detalhes\n")

    def default(self, line):
        """Comando desconhecido"""
        print(f"❌ Comando desconhecido: {line}")
        print("   Digite 'help' para ver os comandos disponíveis")

def main():
    shell = ProteusShell()
    shell.cmdloop()

if __name__ == "__main__":
    main()
