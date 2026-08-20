#!/usr/bin/env python3
"""
ProteusOS - Gerenciador de Configuração
Carrega configurações do arquivo .proteusrc no diretório home.
"""

import json
from pathlib import Path
from typing import Dict, Any

class Config:
    def __init__(self):
        self.config_file = Path.home() / ".proteusrc"
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Carrega a configuração do arquivo .proteusrc"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("⚠️  Arquivo .proteusrc corrompido. Usando configurações padrão.")
                return self._default_config()
        return self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        """Configurações padrão"""
        return {
            "base_dir": str(Path.home() / "proteus_os"),
            "default_image": "alpine",
            "verbose": False,
            "auto_rollback": True
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Retorna o valor de uma configuração"""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Define o valor de uma configuração"""
        self.config[key] = value
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def show(self) -> None:
        """Mostra todas as configurações"""
        print("📋 Configurações atuais:")
        for key, value in self.config.items():
            print(f"   {key}: {value}")

def main():
    """Função para testar a configuração"""
    config = Config()
    config.show()

if __name__ == "__main__":
    main()
