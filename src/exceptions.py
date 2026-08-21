"""
ProteusOS - Exceções Customizadas
"""

class ProteusOSError(Exception):
    """Exceção base para o ProteusOS."""
    pass

class SnapshotError(ProteusOSError):
    """Erro relacionado a snapshots."""
    pass

class SnapshotNotFoundError(SnapshotError):
    """Snapshot não encontrado."""
    pass

class ChecksumMismatchError(SnapshotError):
    """Checksum do snapshot não confere."""
    pass

class PackageError(ProteusOSError):
    """Erro relacionado a pacotes."""
    pass

class PackageNotFoundError(PackageError):
    """Pacote não encontrado."""
    pass

class DependencyError(PackageError):
    """Dependência não satisfeita."""
    pass

class ServiceError(ProteusOSError):
    """Erro relacionado a serviços."""
    pass

class ServiceNotFoundError(ServiceError):
    """Serviço não encontrado."""
    pass

class ISOBuildError(ProteusOSError):
    """Erro na criação da ISO."""
    pass

class ToolNotFoundError(ProteusOSError):
    """Ferramenta externa não encontrada."""
    pass

class ValidationError(ProteusOSError):
    """Erro de validação de entrada."""
    pass
