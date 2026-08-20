#!/usr/bin/env python3
"""
ProteusOS - Init System Manager
Gerencia serviços e processos de inicialização.
"""

import subprocess
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
from logger import get_logger

logger = get_logger()

class InitManager:
    """Gerencia serviços do sistema via systemd ou SysV init."""

    def __init__(self):
        self.logger = get_logger()
        self._detect_init()

    def _detect_init(self):
        """Detecta o sistema de init em uso."""
        if Path("/usr/bin/systemctl").exists():
            self.init_type = "systemd"
        elif Path("/sbin/init").exists():
            self.init_type = "sysv"
        else:
            self.init_type = "unknown"
        self.logger.info(f"Sistema de init detectado: {self.init_type}")

    def enable_service(self, service_name: str) -> bool:
        """Habilita um serviço para iniciar automaticamente."""
        if self.init_type == "systemd":
            return self._systemd_enable(service_name)
        elif self.init_type == "sysv":
            return self._sysv_enable(service_name)
        self.logger.error(f"Init type {self.init_type} not supported")
        return False

    def disable_service(self, service_name: str) -> bool:
        """Desabilita um serviço."""
        if self.init_type == "systemd":
            return self._systemd_disable(service_name)
        elif self.init_type == "sysv":
            return self._sysv_disable(service_name)
        self.logger.error(f"Init type {self.init_type} not supported")
        return False

    def start_service(self, service_name: str) -> bool:
        """Inicia um serviço."""
        if self.init_type == "systemd":
            return self._systemd_start(service_name)
        elif self.init_type == "sysv":
            return self._sysv_start(service_name)
        self.logger.error(f"Init type {self.init_type} not supported")
        return False

    def stop_service(self, service_name: str) -> bool:
        """Para um serviço."""
        if self.init_type == "systemd":
            return self._systemd_stop(service_name)
        elif self.init_type == "sysv":
            return self._sysv_stop(service_name)
        self.logger.error(f"Init type {self.init_type} not supported")
        return False

    def list_services(self) -> List[str]:
        """Lista serviços ativos."""
        if self.init_type == "systemd":
            return self._systemd_list()
        elif self.init_type == "sysv":
            return self._sysv_list()
        self.logger.error(f"Init type {self.init_type} not supported")
        return []

    def _systemd_enable(self, service_name: str) -> bool:
        try:
            subprocess.run(["sudo", "systemctl", "enable", service_name], check=True)
            self.logger.info(f"Serviço habilitado: {service_name}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Erro ao habilitar {service_name}: {e}")
            return False

    def _systemd_disable(self, service_name: str) -> bool:
        try:
            subprocess.run(["sudo", "systemctl", "disable", service_name], check=True)
            self.logger.info(f"Serviço desabilitado: {service_name}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Erro ao desabilitar {service_name}: {e}")
            return False

    def _systemd_start(self, service_name: str) -> bool:
        try:
            subprocess.run(["sudo", "systemctl", "start", service_name], check=True)
            self.logger.info(f"Serviço iniciado: {service_name}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Erro ao iniciar {service_name}: {e}")
            return False

    def _systemd_stop(self, service_name: str) -> bool:
        try:
            subprocess.run(["sudo", "systemctl", "stop", service_name], check=True)
            self.logger.info(f"Serviço parado: {service_name}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Erro ao parar {service_name}: {e}")
            return False

    def _systemd_list(self) -> List[str]:
        try:
            result = subprocess.run(["systemctl", "list-units", "--type=service"], capture_output=True, text=True)
            lines = result.stdout.splitlines()
            services = []
            for line in lines:
                if ".service" in line and "loaded" in line:
                    parts = line.split()
                    if parts:
                        services.append(parts[0])
            return services
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Erro ao listar serviços: {e}")
            return []

    def _sysv_enable(self, service_name: str) -> bool:
        try:
            subprocess.run(["sudo", "update-rc.d", service_name, "defaults"], check=True)
            self.logger.info(f"Serviço habilitado: {service_name}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                subprocess.run(["sudo", "update-rc.d", service_name, "enable"], check=True)
                self.logger.info(f"Serviço habilitado: {service_name}")
                return True
            except Exception as e:
                self.logger.error(f"Erro ao habilitar {service_name}: {e}")
                return False

    def _sysv_disable(self, service_name: str) -> bool:
        try:
            subprocess.run(["sudo", "update-rc.d", service_name, "remove"], check=True)
            self.logger.info(f"Serviço desabilitado: {service_name}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao desabilitar {service_name}: {e}")
            return False

    def _sysv_start(self, service_name: str) -> bool:
        try:
            subprocess.run(["sudo", "service", service_name, "start"], check=True)
            self.logger.info(f"Serviço iniciado: {service_name}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao iniciar {service_name}: {e}")
            return False

    def _sysv_stop(self, service_name: str) -> bool:
        try:
            subprocess.run(["sudo", "service", service_name, "stop"], check=True)
            self.logger.info(f"Serviço parado: {service_name}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao parar {service_name}: {e}")
            return False

    def _sysv_list(self) -> List[str]:
        try:
            result = subprocess.run(["service", "--status-all"], capture_output=True, text=True)
            lines = result.stdout.splitlines()
            services = []
            for line in lines:
                if " " in line:
                    parts = line.split()
                    if parts:
                        services.append(parts[1])
            return services
        except Exception as e:
            self.logger.error(f"Erro ao listar serviços: {e}")
            return []
