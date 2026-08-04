#!/usr/bin/env python3
"""
Gerenciador de Atualizações do ProteusOS
Sistema transacional de atualizações com rollback automático
"""

import os
import shutil
import json
import tempfile
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class SystemUpdater:
    """
    Gerencia atualizações do sistema de forma atômica e transacional
    Cada atualização é aplicada com garantia de rollback em caso de falha
    """
    
    def __init__(self, base_dir: str = "~/proteus_os"):
        """
        Inicializa o atualizador do sistema
        
        Args:
            base_dir: Diretório base do ProteusOS
        """
        self.base_dir = os.path.expanduser(base_dir)
        self.updates_dir = os.path.join(self.base_dir, "updates")
        self.metadata_dir = os.path.join(self.base_dir, "metadata")
        self.index_file = os.path.join(self.metadata_dir, "index.json")
        self.applied_updates_dir = os.path.join(self.updates_dir, "applied")
        
        # Cria diretórios necessários
        os.makedirs(self.updates_dir, exist_ok=True)
        os.makedirs(self.applied_updates_dir, exist_ok=True)
    
    def _load_index(self) -> Dict:
        """Carrega o índice do sistema"""
        if not os.path.exists(self.index_file):
            return {"updates": [], "current_snapshot": None}
        
        with open(self.index_file, 'r') as f:
            return json.load(f)
    
    def _save_index(self, index: Dict):
        """Salva o índice atualizado"""
        with open(self.index_file, 'w') as f:
            json.dump(index, f, indent=2)
    
    def _create_snapshot_from_state(self) -> str:
        """
        Cria um snapshot do estado atual do sistema
        Usa o builder para criar um novo snapshot
        """
        from builder import SystemBuilder
        builder = SystemBuilder(self.base_dir)
        return builder.freeze()
    
    def _apply_update_files(self, update_path: str, snapshot_id: str) -> bool:
        """
        Aplica os arquivos de atualização no sistema
        """
        print(f"[UPDATE] Aplicando atualização: {update_path}")
        
        # Verifica se a atualização tem a estrutura correta
        if not os.path.exists(os.path.join(update_path, "manifest.json")):
            return False
        
        # Carrega o manifesto
        with open(os.path.join(update_path, "manifest.json"), 'r') as f:
            manifest = json.load(f)
        
        # Aplica os arquivos
        files_dir = os.path.join(update_path, "files")
        if not os.path.exists(files_dir):
            return False
        
        for file_change in manifest.get("files", []):
            source = os.path.join(files_dir, file_change["source"])
            dest = file_change["destination"]
            
            if not os.path.exists(source):
                print(f"[UPDATE] Arquivo de origem não encontrado: {source}")
                return False
            
            try:
                # Cria diretório de destino se necessário
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(source, dest)
                
                # Aplica permissões se especificadas
                if "mode" in file_change:
                    os.chmod(dest, file_change["mode"])
            except Exception as e:
                print(f"[UPDATE] Erro ao aplicar arquivo {dest}: {e}")
                return False
        
        return True
    
    def _run_pre_update_script(self, update_path: str) -> bool:
        """Executa scripts pré-atualização"""
        script_path = os.path.join(update_path, "pre_update.sh")
        if os.path.exists(script_path):
            try:
                result = subprocess.run(
                    ["bash", script_path],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(f"[UPDATE] Script pré-atualização executado com sucesso")
                return True
            except subprocess.CalledProcessError as e:
                print(f"[UPDATE] Script pré-atualização falhou: {e.stderr}")
                return False
        return True
    
    def _run_post_update_script(self, update_path: str) -> bool:
        """Executa scripts pós-atualização"""
        script_path = os.path.join(update_path, "post_update.sh")
        if os.path.exists(script_path):
            try:
                result = subprocess.run(
                    ["bash", script_path],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(f"[UPDATE] Script pós-atualização executado com sucesso")
                return True
            except subprocess.CalledProcessError as e:
                print(f"[UPDATE] Script pós-atualização falhou: {e.stderr}")
                return False
        return True
    
    def apply_update(self, update_path: str) -> Tuple[bool, str]:
        """
        Aplica uma atualização de forma transacional
        
        Args:
            update_path: Caminho para o pacote de atualização
        
        Returns:
            (sucesso, mensagem)
        """
        print(f"[UPDATE] Iniciando aplicação de atualização: {update_path}")
        
        if not os.path.exists(update_path):
            return False, f"Atualização não encontrada: {update_path}"
        
        # Salva o snapshot atual para rollback
        old_snapshot = self._load_index().get("current_snapshot")
        if not old_snapshot:
            return False, "Nenhum snapshot atual encontrado"
        
        try:
            # Executa script pré-atualização
            if not self._run_pre_update_script(update_path):
                return False, "Script pré-atualização falhou"
            
            # Cria um novo snapshot de backup
            backup_snapshot = self._create_snapshot_from_state()
            
            # Aplica os arquivos da atualização
            update_id = f"update_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            if not self._apply_update_files(update_path, update_id):
                return False, "Falha ao aplicar arquivos da atualização"
            
            # Executa script pós-atualização
            if not self._run_post_update_script(update_path):
                # Rollback em caso de falha no script pós-atualização
                print("[UPDATE] Falha no script pós-atualização, realizando rollback")
                self.rollback_update(old_snapshot)
                return False, "Script pós-atualização falhou"
            
            # Registra a atualização
            index = self._load_index()
            update_info = {
                "id": update_id,
                "applied_at": datetime.now().isoformat(),
                "from_snapshot": old_snapshot,
                "backup_snapshot": backup_snapshot,
                "update_path": update_path
            }
            
            if "updates" not in index:
                index["updates"] = []
            index["updates"].append(update_info)
            self._save_index(index)
            
            # Remove a atualização aplicada (opcional)
            # shutil.rmtree(update_path)
            
            print(f"[UPDATE] Atualização aplicada com sucesso: {update_id}")
            return True, f"Atualização aplicada com sucesso: {update_id}"
            
        except Exception as e:
            print(f"[UPDATE] Erro durante atualização: {e}")
            self.rollback_update(old_snapshot)
            return False, f"Erro durante atualização: {str(e)}"
    
    def rollback_update(self, target_snapshot: str = None) -> Tuple[bool, str]:
        """
        Reverte para um snapshot anterior
        
        Args:
            target_snapshot: ID do snapshot para reverter (opcional)
        
        Returns:
            (sucesso, mensagem)
        """
        print(f"[UPDATE] Realizando rollback para snapshot: {target_snapshot}")
        
        index = self._load_index()
        current_snapshot = index.get("current_snapshot")
        
        # Se não especificado, usa o snapshot anterior
        if not target_snapshot:
            updates = index.get("updates", [])
            if not updates:
                return False, "Nenhuma atualização anterior encontrada"
            
            # Usa o backup_snapshot da última atualização
            last_update = updates[-1]
            target_snapshot = last_update.get("backup_snapshot")
            
            if not target_snapshot:
                return False, "Snapshot de backup não encontrado"
        
        # Verifica se o snapshot de destino existe
        from builder import SystemBuilder
        builder = SystemBuilder(self.base_dir)
        if not builder.validate_snapshot(target_snapshot):
            return False, f"Snapshot inválido ou não encontrado: {target_snapshot}"
        
        # Atualiza o índice para o snapshot de destino
        index["current_snapshot"] = target_snapshot
        index["last_rollback"] = {
            "from": current_snapshot,
            "to": target_snapshot,
            "at": datetime.now().isoformat()
        }
        
        self._save_index(index)
        
        # Registra a operação de rollback
        self._record_rollback(current_snapshot, target_snapshot)
        
        print(f"[UPDATE] Rollback realizado com sucesso para: {target_snapshot}")
        return True, f"Rollback realizado para snapshot: {target_snapshot}"
    
    def _record_rollback(self, from_snapshot: str, to_snapshot: str):
        """Registra um rollback no histórico"""
        from pkg_manager import PackageManager
        pkg_manager = PackageManager(self.base_dir)
        pkg_manager._record_operation({
            "type": "rollback",
            "from_snapshot": from_snapshot,
            "to_snapshot": to_snapshot
        })
    
    def list_updates(self) -> List[Dict]:
        """Lista todas as atualizações aplicadas"""
        index = self._load_index()
        return index.get("updates", [])
    
    def get_update_info(self, update_id: str) -> Optional[Dict]:
        """Obtém informações de uma atualização específica"""
        index = self._load_index()
        for update in index.get("updates", []):
            if update["id"] == update_id:
                return update
        return None
    
    def get_available_updates(self) -> List[str]:
        """Lista atualizações disponíveis para aplicação"""
        # Procura por diretórios de atualização não aplicados
        available = []
        for item in os.listdir(self.updates_dir):
            item_path = os.path.join(self.updates_dir, item)
            if os.path.isdir(item_path) and item != "applied":
                # Verifica se já foi aplicado
                index = self._load_index()
                if not any(u.get("update_path") == item_path for u in index.get("updates", [])):
                    available.append(item_path)
        return available