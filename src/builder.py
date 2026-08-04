#!/usr/bin/env python3
"""
Gerenciador de Estado e Build do ProteusOS
Responsável por criar snapshots do sistema e gerenciar o estado atual
"""

import os
import shutil
import tarfile
import json
import hashlib
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List

class SystemBuilder:
    """
    Gerencia a criação e versionamento de snapshots do sistema
    Similar ao ostree, cada snapshot é uma imagem completa do sistema
    """
    
    def __init__(self, base_dir: str = "~/proteus_os"):
        """
        Inicializa o SystemBuilder com o diretório base
        
        Args:
            base_dir: Diretório raiz onde os dados do ProteusOS serão armazenados
        """
        self.base_dir = os.path.expanduser(base_dir)
        self.snapshots_dir = os.path.join(self.base_dir, "snapshots")
        self.metadata_dir = os.path.join(self.base_dir, "metadata")
        self.updates_dir = os.path.join(self.base_dir, "updates")
        self.index_file = os.path.join(self.metadata_dir, "index.json")
        self.snapshot_base = os.path.join(self.base_dir, "snapshot_work")
        
        # Cria a estrutura de diretórios se não existir
        self._create_directories()
        
        # Inicializa o índice se não existir
        if not os.path.exists(self.index_file):
            self._initialize_index()
    
    def _create_directories(self):
        """Cria todos os diretórios necessários para o sistema"""
        for directory in [self.snapshots_dir, self.metadata_dir, self.updates_dir, self.snapshot_base]:
            os.makedirs(directory, exist_ok=True)
    
    def _initialize_index(self):
        """Inicializa o arquivo de índice com valores padrão"""
        index = {
            "current_snapshot": None,
            "snapshots": [],
            "updates_history": [],
            "version": 0,
            "created_at": datetime.now().isoformat()
        }
        with open(self.index_file, 'w') as f:
            json.dump(index, f, indent=2)
    
    def _load_index(self) -> Dict:
        """Carrega o índice atual do sistema"""
        with open(self.index_file, 'r') as f:
            return json.load(f)
    
    def _save_index(self, index: Dict):
        """Salva o índice atualizado no arquivo"""
        with open(self.index_file, 'w') as f:
            json.dump(index, f, indent=2)
    
    def _calculate_checksum(self, filepath: str) -> str:
        """Calcula o checksum SHA256 de um arquivo"""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _get_snapshot_path(self, snapshot_id: str) -> str:
        """Retorna o caminho completo para um snapshot"""
        return os.path.join(self.snapshots_dir, f"snapshot_{snapshot_id}.tar.gz")
    
    def build_system(self, base_image: str = "alpine") -> str:
        """
        Constrói uma nova imagem do sistema
        
        Args:
            base_image: Imagem base a ser usada (alpine ou debian)
        
        Returns:
            ID do snapshot criado
        """
        print(f"[BUILD] Construindo nova imagem base: {base_image}")
        
        # Limpa o diretório de trabalho
        if os.path.exists(self.snapshot_base):
            shutil.rmtree(self.snapshot_base)
        os.makedirs(self.snapshot_base)
        
        # Simula a criação de um sistema base
        if base_image == "alpine":
            self._build_alpine_base()
        elif base_image == "debian":
            self._build_debian_base()
        else:
            raise ValueError(f"Imagem base não suportada: {base_image}")
        
        # Gera um novo ID de snapshot
        snapshot_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{base_image}"
        snapshot_path = self._get_snapshot_path(snapshot_id)
        
        # Cria o arquivo tar.gz do snapshot
        print(f"[BUILD] Criando snapshot {snapshot_id}")
        with tarfile.open(snapshot_path, "w:gz") as tar:
            tar.add(self.snapshot_base, arcname=".")
        
        # Calcula checksum
        checksum = self._calculate_checksum(snapshot_path)
        
        # Atualiza o índice
        index = self._load_index()
        snapshot_info = {
            "id": snapshot_id,
            "created_at": datetime.now().isoformat(),
            "base_image": base_image,
            "checksum": checksum,
            "size": os.path.getsize(snapshot_path)
        }
        
        index["snapshots"].append(snapshot_info)
        index["current_snapshot"] = snapshot_id
        index["version"] += 1
        self._save_index(index)
        
        print(f"[BUILD] Snapshot criado com sucesso: {snapshot_id}")
        return snapshot_id
    
    def _build_alpine_base(self):
        """Simula a construção de uma base Alpine Linux"""
        # Cria estrutura básica de diretórios
        for dir_path in ["bin", "etc", "home", "lib", "usr", "var", "root"]:
            os.makedirs(os.path.join(self.snapshot_base, dir_path), exist_ok=True)
        
        # Cria alguns arquivos de sistema simulados
        etc_path = os.path.join(self.snapshot_base, "etc")
        with open(os.path.join(etc_path, "alpine-release"), 'w') as f:
            f.write("3.18.0\n")
        
        with open(os.path.join(etc_path, "hostname"), 'w') as f:
            f.write("proteus-os\n")
        
        # Simula arquivos de sistema essenciais
        bin_path = os.path.join(self.snapshot_base, "bin")
        with open(os.path.join(bin_path, "sh"), 'w') as f:
            f.write("#!/bin/sh\necho 'ProteusOS Shell'\n")
        os.chmod(os.path.join(bin_path, "sh"), 0o755)
    
    def _build_debian_base(self):
        """Simula a construção de uma base Debian"""
        # Cria estrutura básica de diretórios
        for dir_path in ["bin", "etc", "home", "lib", "usr", "var", "root", "opt", "mnt"]:
            os.makedirs(os.path.join(self.snapshot_base, dir_path), exist_ok=True)
        
        # Cria alguns arquivos de sistema simulados
        etc_path = os.path.join(self.snapshot_base, "etc")
        with open(os.path.join(etc_path, "debian_version"), 'w') as f:
            f.write("12.1\n")
        
        with open(os.path.join(etc_path, "hostname"), 'w') as f:
            f.write("proteus-os\n")
        
        # Simula arquivos de sistema essenciais
        bin_path = os.path.join(self.snapshot_base, "bin")
        with open(os.path.join(bin_path, "bash"), 'w') as f:
            f.write("#!/bin/bash\necho 'ProteusOS Bash'\n")
        os.chmod(os.path.join(bin_path, "bash"), 0o755)
    
    def freeze(self) -> str:
        """
        Congela o estado atual do sistema em um snapshot
        
        Returns:
            ID do snapshot criado
        """
        print("[FREEZE] Congelando estado atual do sistema")
        
        index = self._load_index()
        current_snapshot = index.get("current_snapshot")
        
        if not current_snapshot:
            raise ValueError("Nenhum snapshot atual para congelar")
        
        # Cria um novo snapshot a partir do atual
        current_path = self._get_snapshot_path(current_snapshot)
        snapshot_id = f"frozen_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        frozen_path = self._get_snapshot_path(snapshot_id)
        
        # Copia o snapshot atual
        shutil.copy2(current_path, frozen_path)
        
        # Atualiza o índice
        snapshot_info = {
            "id": snapshot_id,
            "created_at": datetime.now().isoformat(),
            "base_image": "frozen",
            "checksum": self._calculate_checksum(frozen_path),
            "size": os.path.getsize(frozen_path),
            "frozen_from": current_snapshot
        }
        
        index["snapshots"].append(snapshot_info)
        self._save_index(index)
        
        print(f"[FREEZE] Snapshot congelado: {snapshot_id}")
        return snapshot_id
    
    def get_current_snapshot(self) -> Optional[str]:
        """Retorna o ID do snapshot atual"""
        index = self._load_index()
        return index.get("current_snapshot")
    
    def list_snapshots(self) -> List[str]:
        """Lista todos os snapshots disponíveis"""
        index = self._load_index()
        return [s["id"] for s in index.get("snapshots", [])]
    
    def get_snapshot_info(self, snapshot_id: str) -> Optional[Dict]:
        """Obtém informações detalhadas de um snapshot"""
        index = self._load_index()
        for snapshot in index.get("snapshots", []):
            if snapshot["id"] == snapshot_id:
                return snapshot
        return None
    
    def validate_snapshot(self, snapshot_id: str) -> bool:
        """Valida a integridade de um snapshot"""
        snapshot_path = self._get_snapshot_path(snapshot_id)
        
        if not os.path.exists(snapshot_path):
            return False
        
        # Verifica se o tar.gz é válido
        try:
            with tarfile.open(snapshot_path, "r:gz") as tar:
                # Verifica se o arquivo é um tar válido
                tar.getmembers()
        except Exception:
            return False
        
        # Verifica checksum
        info = self.get_snapshot_info(snapshot_id)
        if info:
            computed_checksum = self._calculate_checksum(snapshot_path)
            return computed_checksum == info.get("checksum")
        
        return True