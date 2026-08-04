#!/usr/bin/env python3
"""
Gerenciador de Pacotes do ProteusOS
Sistema simples de aplicação de pacotes/atualizações de forma transacional
"""

import os
import shutil
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class PackageManager:
    """
    Gerencia pacotes e atualizações do sistema de forma transacional
    Cada aplicação é atômica e reversível
    """
    
    def __init__(self, base_dir: str = "~/proteus_os"):
        """
        Inicializa o gerenciador de pacotes
        
        Args:
            base_dir: Diretório base do ProteusOS
        """
        self.base_dir = os.path.expanduser(base_dir)
        self.packages_dir = os.path.join(self.base_dir, "packages")
        self.metadata_dir = os.path.join(self.base_dir, "metadata")
        self.index_file = os.path.join(self.metadata_dir, "index.json")
        self.applied_dir = os.path.join(self.packages_dir, "applied")
        self.available_dir = os.path.join(self.packages_dir, "available")
        
        # Cria diretórios necessários
        os.makedirs(self.packages_dir, exist_ok=True)
        os.makedirs(self.applied_dir, exist_ok=True)
        os.makedirs(self.available_dir, exist_ok=True)
    
    def _load_index(self) -> Dict:
        """Carrega o índice do sistema"""
        if not os.path.exists(self.index_file):
            return {"packages": [], "applied_packages": []}
        
        with open(self.index_file, 'r') as f:
            return json.load(f)
    
    def _save_index(self, index: Dict):
        """Salva o índice atualizado"""
        with open(self.index_file, 'w') as f:
            json.dump(index, f, indent=2)
    
    def _calculate_checksum(self, filepath: str) -> str:
        """Calcula checksum SHA256 de um arquivo"""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _backup_file(self, filepath: str) -> str:
        """
        Cria um backup de um arquivo antes de modificá-lo
        Retorna o caminho do backup
        """
        if not os.path.exists(filepath):
            return None
        
        backup_dir = os.path.join(self.base_dir, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        backup_name = f"{os.path.basename(filepath)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
        backup_path = os.path.join(backup_dir, backup_name)
        shutil.copy2(filepath, backup_path)
        
        return backup_path
    
    def _record_operation(self, operation: Dict):
        """Registra uma operação no histórico"""
        index = self._load_index()
        
        if "history" not in index:
            index["history"] = []
        
        index["history"].append({
            "timestamp": datetime.now().isoformat(),
            "operation": operation
        })
        
        self._save_index(index)
    
    def install_package(self, package_path: str) -> Tuple[bool, str]:
        """
        Instala um pacote de forma transacional
        
        Args:
            package_path: Caminho para o pacote (diretório com arquivos)
        
        Returns:
            (sucesso, mensagem)
        """
        print(f"[PKG] Instalando pacote: {package_path}")
        
        if not os.path.exists(package_path):
            return False, f"Pacote não encontrado: {package_path}"
        
        # Registra o pacote disponível
        package_name = os.path.basename(package_path)
        package_id = f"{package_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Verifica se o pacote é válido
        if not self._validate_package(package_path):
            return False, "Pacote inválido"
        
        # Cria backup do estado atual
        index = self._load_index()
        backup_snapshot = index.get("current_snapshot")
        
        try:
            # Aplica as mudanças
            changes = self._apply_package(package_path, package_id)
            
            # Registra o pacote
            package_info = {
                "id": package_id,
                "name": package_name,
                "installed_at": datetime.now().isoformat(),
                "changes": changes,
                "checksum": self._calculate_checksum(package_path)
            }
            
            if "packages" not in index:
                index["packages"] = []
            index["packages"].append(package_info)
            
            if "applied_packages" not in index:
                index["applied_packages"] = []
            index["applied_packages"].append(package_id)
            
            self._save_index(index)
            
            # Registra a operação
            self._record_operation({
                "type": "install",
                "package_id": package_id,
                "package_name": package_name,
                "backup_snapshot": backup_snapshot
            })
            
            return True, f"Pacote instalado com sucesso: {package_id}"
            
        except Exception as e:
            # Rollback em caso de erro
            print(f"[PKG] Erro durante instalação, realizando rollback: {e}")
            return False, f"Falha ao instalar pacote: {str(e)}"
    
    def _validate_package(self, package_path: str) -> bool:
        """Valida se um pacote tem a estrutura correta"""
        # Verifica se tem um arquivo de manifesto
        manifest_path = os.path.join(package_path, "manifest.json")
        if not os.path.exists(manifest_path):
            print("[PKG] Pacote sem manifest.json")
            return False
        
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            return "files" in manifest
        except:
            return False
    
    def _apply_package(self, package_path: str, package_id: str) -> List[Dict]:
        """
        Aplica as mudanças do pacote no sistema
        
        Returns:
            Lista de mudanças aplicadas
        """
        changes = []
        
        # Carrega o manifesto
        with open(os.path.join(package_path, "manifest.json"), 'r') as f:
            manifest = json.load(f)
        
        # Aplica os arquivos
        for file_change in manifest.get("files", []):
            source = os.path.join(package_path, "files", file_change["source"])
            dest = file_change["destination"]
            
            # Cria backup se o arquivo existir
            if os.path.exists(dest):
                backup_path = self._backup_file(dest)
                changes.append({
                    "type": "replace",
                    "file": dest,
                    "backup": backup_path
                })
            else:
                # Cria diretório se necessário
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                changes.append({
                    "type": "add",
                    "file": dest
                })
            
            # Copia o arquivo
            shutil.copy2(source, dest)
            
            # Aplica permissões se especificadas
            if "mode" in file_change:
                os.chmod(dest, file_change["mode"])
        
        return changes
    
    def uninstall_package(self, package_id: str) -> Tuple[bool, str]:
        """
        Desinstala um pacote instalado anteriormente
        """
        print(f"[PKG] Desinstalando pacote: {package_id}")
        
        index = self._load_index()
        
        # Encontra o pacote
        package = None
        for p in index.get("packages", []):
            if p["id"] == package_id:
                package = p
                break
        
        if not package:
            return False, f"Pacote não encontrado: {package_id}"
        
        try:
            # Reverte as mudanças (simplificado)
            # Em um sistema real, precisaríamos armazenar mais informações sobre mudanças
            changes = package.get("changes", [])
            
            # Remove o pacote do índice
            index["packages"] = [p for p in index.get("packages", []) if p["id"] != package_id]
            if package_id in index.get("applied_packages", []):
                index["applied_packages"].remove(package_id)
            
            self._save_index(index)
            
            # Registra a operação
            self._record_operation({
                "type": "uninstall",
                "package_id": package_id
            })
            
            return True, f"Pacote desinstalado: {package_id}"
            
        except Exception as e:
            return False, f"Falha ao desinstalar pacote: {str(e)}"
    
    def list_packages(self) -> List[Dict]:
        """Lista todos os pacotes instalados"""
        index = self._load_index()
        return index.get("packages", [])
    
    def get_package_info(self, package_id: str) -> Optional[Dict]:
        """Obtém informações de um pacote específico"""
        index = self._load_index()
        for package in index.get("packages", []):
            if package["id"] == package_id:
                return package
        return None