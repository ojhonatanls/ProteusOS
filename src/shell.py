#!/usr/bin/env python3
"""
ProteusOS - Interactive Shell
"""

import cmd
import sys
from pathlib import Path

src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

from cli import ProteusCLI

class ProteusShell(cmd.Cmd):
    intro = """
╔═══════════════════════════════════════════╗
║   ProteusOS - Interactive Shell          ║
║   Type 'help' to see available commands  ║
║   Type 'exit' or 'quit' to exit          ║
╚═══════════════════════════════════════════╝
"""
    prompt = "proteus> "

    def __init__(self):
        super().__init__()
        self.cli = ProteusCLI()

    def do_build(self, arg):
        """Build a base system: build --base-image alpine"""
        if not arg:
            print("Usage: build --base-image alpine|debian")
            return
        self.cli.run(["build"] + arg.split())

    def do_status(self, arg):
        """View system status"""
        self.cli.run(["status"])

    def do_update(self, arg):
        """Apply an update: update /path/to/update"""
        if not arg:
            print("Usage: update /path/to/update")
            return
        self.cli.run(["update", arg])

    def do_rollback(self, arg):
        """Rollback to a snapshot: rollback [--snapshot-id ID]"""
        if arg:
            self.cli.run(["rollback", "--snapshot-id", arg])
        else:
            self.cli.run(["rollback"])

    def do_package(self, arg):
        """Manage packages: package install|list|uninstall [args]"""
        if not arg:
            print("Usage: package install|list|uninstall [args]")
            return
        self.cli.run(["package"] + arg.split())

    def do_pts(self, arg):
        """Universal package manager: pts install|remove|list|search [args]"""
        if not arg:
            print("Usage: pts install|remove|list|search [args]")
            return
        self.cli.run(["pts"] + arg.split())

    def do_service(self, arg):
        """Manage services: service list|start|stop|enable|disable [name]"""
        if not arg:
            print("Usage: service list|start|stop|enable|disable [name]")
            return
        self.cli.run(["service"] + arg.split())

    def do_distro_build(self, arg):
        """Build a bootable ISO: distro-build --snapshot-id ID --kernel /path/to/vmlinuz [--output file.iso]"""
        if not arg:
            print("Usage: distro-build --snapshot-id ID --kernel /path/to/vmlinuz [--output file.iso]")
            return
        self.cli.run(["distro-build"] + arg.split())

    def do_clear(self, arg):
        """Clear the screen"""
        print("\033c", end="")

    def do_exit(self, arg):
        """Exit the shell"""
        print("Goodbye!")
        return True

    def do_quit(self, arg):
        """Exit the shell"""
        return self.do_exit(arg)

    def do_help(self, arg):
        """Show help about commands"""
        if arg:
            super().do_help(arg)
        else:
            print("\nAvailable commands:")
            print("   build         - Build a base system")
            print("   status        - View system status")
            print("   update        - Apply an update")
            print("   rollback      - Rollback to a snapshot")
            print("   package       - Manage packages (native)")
            print("   pts           - Universal package manager")
            print("   service       - Manage system services")
            print("   distro-build  - Build a bootable ISO")
            print("   clear         - Clear the screen")
            print("   exit          - Exit the shell")
            print("   quit          - Exit the shell")
            print("\nType 'help <command>' for more details\n")

    def default(self, line):
        """Unknown command"""
        print(f"Unknown command: {line}")
        print("   Type 'help' to see available commands")

def main():
    shell = ProteusShell()
    shell.cmdloop()

if __name__ == "__main__":
    main()
