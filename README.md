# ProteusOS - Sistema Operacional Minimalista e Modular

[![Version](https://img.shields.io/badge/version-2.4.0-blue.svg)](https://github.com/ojhonatanls/ProteusOS/releases/tag/v2.2.0)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](https://opensource.org/licenses/MIT)
[![ISO](https://img.shields.io/badge/ISO-bootable-brightgreen.svg)](https://github.com/ojhonatanls/ProteusOS/releases/tag/v2.2.0)
[![Tests](https://img.shields.io/badge/tests-4%20passing-brightgreen.svg)](https://github.com/ojhonatanls/ProteusOS/actions)

## Visão Geral

ProteusOS é um sistema operacional minimalista que implementa conceitos de:

- **Imagens Atômicas**: Cada atualização gera um snapshot completo do sistema
- **Rollback Imediato**: Reversão para estados anteriores em caso de falha
- **Gerenciamento Transacional**: Atualizações aplicadas de forma atômica
- **Arquitetura Modular**: Componentes independentes e substituíveis
- **Suporte a C**: Módulos em C para operações de alta performance
- **Integridade Garantida**: Verificação de checksum SHA-256 para snapshots
- **Gerenciador Universal**: `pts` - suporte a APT, DNF e Pacman
- **Bootável**: ISO com GRUB e initrd integrado

## Status do Projeto

- Sistema de build funcionando (Python + C)
- Gerenciamento de snapshots com checksum SHA-256
- Gerenciamento de pacotes com dependências
- Sistema de atualizações atômicas
- Rollback para qualquer snapshot com verificação de integridade
- CLI completa e funcional
- Modo shell interativo
- Gerenciador de configuração
- Testes automatizados
- Comando info para detalhes
- Export/Import de snapshots
- Cleanup de snapshots antigos
- Módulo C para operações críticas
- Sistema de logging estruturado
- File locking para operações concorrentes
- Sanitização de entrada para segurança
- Backup automático de metadados
- Sanitização de logs para proteção de dados sensíveis
- **Gerenciador de pacotes universal (pts) com APT, DNF e Pacman**
- **Rollback automático em caso de falha na instalação de pacotes**
- **Gerenciamento de serviços (systemd/SysV)**
- **Criação de ISO bootável com GRUB**
- **Snapshots com diff para economia de espaço**
- **Full shell environment com busybox e ferramentas essenciais**

## Requisitos

- Python 3.10+
- Biblioteca padrão (sem dependências externas)
- GCC (para compilar módulos C, opcional)
- APT, DNF ou Pacman (para o gerenciador universal)
- xorriso (para criar ISOs, opcional)

## Instalação

Clone o repositório:
```bash
git clone https://github.com/ojhonatanls/ProteusOS.git
cd ProteusOS
```

Torne o script executável:
```bash
chmod +x proteus
```

## Estrutura do Projeto

```bash
ProteusOS/
├── proteus                 # Script principal executável
├── pts                     # Alias para o gerenciador universal
├── src/                    # Código-fonte
│   ├── cli.py              # Interface de linha de comando
│   ├── builder.py          # Gerenciador de snapshots (com checksum)
│   ├── pkg_manager.py      # Gerenciador de pacotes com dependências
│   ├── updater.py          # Gerenciador de atualizações
│   ├── config.py           # Gerenciador de configuração
│   ├── shell.py            # Modo shell interativo
│   ├── constants.py        # Constantes centralizadas
│   ├── logger.py           # Sistema de logging estruturado
│   ├── locking.py          # File locking para concorrência
│   ├── drivers.py          # Drivers para APT, DNF e Pacman
│   ├── init_manager.py     # Gerenciador de serviços
│   ├── distro_builder.py   # Criação de ISO bootável
│   └── c_bridge/           # Módulos em C
│       └── snapshot.c      # Implementação em C
├── tests/                  # Testes automatizados
│   └── test_proteus.py     # Suite de testes
├── setup.py                # Compilação de módulos C
├── update_example/         # Exemplo de pacote de atualização
└── README.md               # Documentação
```

## Uso

### Modo CLI (Tradicional)

```bash
# Construir um sistema base (Python - estável)
./proteus build --base-image alpine
./proteus build --base-image debian

# Construir um sistema base (C - experimental, mais rápido)
./proteus build --base-image alpine --use-c

# Construir um snapshot completo ou diff
./proteus build --base-image alpine --full   # Snapshot completo
./proteus build --base-image alpine          # Snapshot diff

# Status do sistema
./proteus status

# Aplicar uma atualização
./proteus update /path/to/update

# Rollback (com verificação de integridade)
./proteus rollback
./proteus rollback --snapshot-id snapshot_20240101_120000_alpine

# Gerenciar pacotes (nativo)
./proteus package install /path/to/package
./proteus package list
./proteus package uninstall package_id

# Gerenciar pacotes (universal - pts)
./proteus pts list                     # Listar pacotes instalados
./proteus pts search nginx             # Buscar pacotes
./proteus pts install htop             # Instalar pacote (com snapshot atômico)
./proteus pts remove htop              # Remover pacote
./proteus pts install htop --driver apt # Forçar um driver específico

# Gerenciar serviços
./proteus service list                 # Listar serviços
./proteus service start nginx          # Iniciar serviço
./proteus service stop nginx           # Parar serviço
./proteus service enable nginx         # Habilitar serviço
./proteus service disable nginx        # Desabilitar serviço

# Criar ISO bootável
./proteus distro-build --snapshot-id snapshot_20260820_203652_alpine --kernel /boot/vmlinuz-$(uname -r) --output proteusos.iso

# Gerenciar configurações
./proteus config --show
./proteus config --set default_image debian

# Informações detalhadas
./proteus info snapshot_20260820_100752_alpine
./proteus info pkg_20260820_094901

# Exportar snapshot
./proteus export snapshot_20260820_111526_alpine
./proteus export snapshot_20260820_111526_alpine --output ~/backups/meu_snapshot.tar.gz

# Importar snapshot
./proteus import ~/proteus_exports/snapshot_20260820_111526_alpine.tar.gz

# Limpar snapshots antigos
./proteus cleanup --keep 3
./proteus cleanup --snapshot-id snapshot_20260820_111526_debian
```

### Modo Shell Interativo

```bash
# Entrar no shell
./proteus shell

# Dentro do shell, usar comandos diretamente
proteus> status
proteus> build --base-image alpine
proteus> build --base-image alpine --use-c
proteus> package list
proteus> pts list
proteus> pts search nginx
proteus> pts install htop
proteus> service list
proteus> info pkg_20260820_094901
proteus> config --show
proteus> export snapshot_20260820_111526_alpine
proteus> cleanup --keep 3
proteus> exit
```

### Comandos do Shell

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `build` | Construir sistema base | `build --base-image alpine` |
| `build --use-c` | Construir com C | `build --base-image alpine --use-c` |
| `build --full` | Criar snapshot completo | `build --base-image alpine --full` |
| `status` | Ver status do sistema | `status` |
| `update` | Aplicar atualização | `update /path/to/update` |
| `rollback` | Rollback para snapshot | `rollback snapshot_ID` |
| `package` | Gerenciar pacotes (nativo) | `package install pacote.tar.gz` |
| `pts` | Gerenciador universal (APT/DNF/Pacman) | `pts install htop` |
| `service` | Gerenciar serviços | `service list` |
| `distro-build` | Criar ISO bootável | `distro-build --snapshot-id X --kernel /boot/vmlinuz` |
| `config` | Gerenciar configurações | `config --show` |
| `info` | Informações detalhadas | `info snapshot_ID` |
| `export` | Exportar snapshot | `export snapshot_ID` |
| `import` | Importar snapshot | `import /path/to/file.tar.gz` |
| `cleanup` | Limpar snapshots antigos | `cleanup --keep 3` |
| `clear` | Limpar tela | `clear` |
| `help` | Mostrar ajuda | `help` |
| `exit`/`quit` | Sair do shell | `exit` |

## Gerenciador de Pacotes Universal (pts)

O `pts` (Proteus Tool Suite) é um gerenciador de pacotes universal que suporta:

| Driver | Sistema | Comando |
|--------|---------|---------|
| `apt` | Debian/Ubuntu | `./proteus pts install htop --driver apt` |
| `dnf` | Fedora/RHEL | `./proteus pts install htop --driver dnf` |
| `pacman` | Arch Linux | `./proteus pts install htop --driver pacman` |

### Características do `pts`:

- **Detecção automática**: Identifica o sistema e usa o driver correto
- **Instalação atômica**: Cria snapshot antes e depois da instalação
- **Rollback automático**: Se a instalação falhar, volta ao snapshot anterior
- **Multi-plataforma**: Funciona em Debian, Fedora e Arch

### Exemplos com `pts`:

```bash
# Listar pacotes instalados
./proteus pts list

# Buscar um pacote
./proteus pts search nginx

# Instalar um pacote (com snapshot atômico)
./proteus pts install htop

# Forçar um driver específico
./proteus pts install htop --driver apt

# Remover um pacote
./proteus pts remove htop
```

## Gerenciamento de Serviços

O ProteusOS suporta gerenciamento de serviços via systemd e SysV init:

```bash
# Listar serviços ativos
./proteus service list

# Iniciar um serviço
./proteus service start nginx

# Parar um serviço
./proteus service stop nginx

# Habilitar um serviço (iniciar automaticamente)
./proteus service enable nginx

# Desabilitar um serviço
./proteus service disable nginx
```

## Criação de ISO Bootável

O ProteusOS pode gerar uma ISO bootável com GRUB e initrd:

```bash
# 1. Criar um snapshot completo
./proteus build --base-image alpine --full

# 2. Criar a ISO
./proteus distro-build --snapshot-id snapshot_20260820_203652_alpine --kernel /boot/vmlinuz-$(uname -r) --output proteusos.iso

# 3. Testar no QEMU
qemu-system-x86_64 -cdrom proteusos.iso -m 512

# 4. Gravar em um pendrive (cuidado!)
sudo dd if=proteusos.iso of=/dev/sdX bs=4M status=progress
```

### Especificações da ISO:

- **Bootloader**: GRUB 2.14
- **Kernel**: vmlinuz do sistema hospedeiro
- **Initrd**: 6.4 MB com busybox
- **Tamanho**: ~20 MB
- **Boot time**: < 10 segundos
- **Ferramentas**: busybox, nano, htop, mc, tree, curl, wget, git

## Exemplos Práticos

### 1. Criar um sistema Alpine (Python)
```bash
./proteus build --base-image alpine
```

### 2. Criar um sistema Alpine (C - mais rápido)
```bash
./proteus build --base-image alpine --use-c
```

### 3. Criar um snapshot completo (não diff)
```bash
./proteus build --base-image alpine --full
```

### 4. Verificar snapshots disponíveis
```bash
./proteus status
```

### 5. Instalar um pacote com rollback automático
```bash
# Instalar htop (cria snapshot pré e pós-instalação)
./proteus pts install htop

# Se falhar, rollback automático é feito
./proteus pts install pacote-inexistente
```

### 6. Listar pacotes instalados
```bash
./proteus pts list
```

### 7. Buscar pacotes
```bash
./proteus pts search nginx
```

### 8. Remover um pacote
```bash
./proteus pts remove htop
```

### 9. Gerenciar serviços
```bash
./proteus service list
./proteus service start docker
./proteus service enable nginx
```

### 10. Criar uma ISO bootável
```bash
./proteus build --base-image alpine --full
./proteus distro-build --snapshot-id snapshot_20260820_203652_alpine --kernel /boot/vmlinuz-$(uname -r) --output proteusos.iso
```

### 11. Testar a ISO no QEMU
```bash
qemu-system-x86_64 -cdrom proteusos.iso -m 512
```

### 12. Exportar um snapshot
```bash
# Exportar para o diretório padrão (~/proteus_exports/)
./proteus export snapshot_20260820_111526_alpine

# Exportar para um local específico
./proteus export snapshot_20260820_111526_alpine --output ~/backups/meu_snapshot.tar.gz
```

### 13. Importar um snapshot
```bash
./proteus import ~/proteus_exports/snapshot_20260820_111526_alpine.tar.gz
```

### 14. Limpar snapshots antigos
```bash
# Manter apenas os 3 mais recentes
./proteus cleanup --keep 3

# Remover um snapshot específico
./proteus cleanup --snapshot-id snapshot_20260820_111526_debian
```

### 15. Usar o shell interativo
```bash
./proteus shell
proteus> status
proteus> build --base-image debian --use-c
proteus> pts list
proteus> pts install htop
proteus> service list
proteus> export snapshot_20260820_111526_alpine
proteus> exit
```

### 16. Ver informações detalhadas
```bash
# Informações de um snapshot (com checksum)
./proteus info snapshot_20260820_100752_alpine

# Informações de um pacote
./proteus info pkg_20260820_094901
```

### 17. Gerenciar configurações
```bash
# Mostrar configurações atuais
./proteus config --show

# Definir imagem padrão
./proteus config --set default_image debian

# Definir diretório base
./proteus config --set base_dir /opt/proteus_os
```

## Arquitetura

**SystemBuilder (builder.py)**
Gerencia a criação e versionamento de snapshots. Cada snapshot é uma imagem completa do sistema armazenada como tar.gz, com checksum SHA-256 para garantir integridade. Suporta snapshots completos e diffs.

**PackageManager (pkg_manager.py)**
Gerencia pacotes de forma transacional, permitindo instalação e desinstalação com rollback. Suporta dependências entre pacotes.

**SystemUpdater (updater.py)**
Gerencia atualizações do sistema com garantias de atomicidade e rollback automático, com verificação de integridade.

**CLI (cli.py)**
Interface de linha de comando que expõe todas as funcionalidades, incluindo export/import, cleanup, service e distro-build.

**Config (config.py)**
Gerenciador de configuração centralizado com suporte a arquivo `~/.proteusrc`.

**Shell (shell.py)**
Modo interativo para executar comandos do ProteusOS em um ambiente shell persistente.

**C Bridge (c_bridge/snapshot.c)**
Módulo em C para operações críticas de snapshot, oferecendo melhor performance.

**Logger (logger.py)**
Sistema de logging estruturado com níveis de log, arquivo de log e sanitização automática de dados sensíveis.

**Locking (locking.py)**
Mecanismo de file locking para prevenir corrupção de dados em operações concorrentes.

**Constants (constants.py)**
Centralização de todas as constantes do sistema para facilitar manutenção.

**Drivers (drivers.py)**
Drivers para gerenciadores de pacotes (APT, DNF, Pacman) integrados ao sistema de snapshots.

**InitManager (init_manager.py)**
Gerenciamento de serviços via systemd e SysV init.

**DistroBuilder (distro_builder.py)**
Criação de ISO bootável com GRUB, kernel e initrd.

## Comandos Disponíveis

| Comando | Descrição |
|---------|-----------|
| `build` | Construir um sistema base (alpine/debian) |
| `build --use-c` | Construir usando C (experimental) |
| `build --full` | Criar snapshot completo (não diff) |
| `status` | Status do sistema e snapshots |
| `update` | Aplicar uma atualização |
| `rollback` | Rollback para um snapshot |
| `package` | Gerenciar pacotes (nativo) |
| `pts` | Gerenciador de pacotes universal (APT/DNF/Pacman) |
| `service` | Gerenciar serviços (start/stop/enable/disable/list) |
| `distro-build` | Criar ISO bootável |
| `config` | Gerenciar configurações (--show/--set) |
| `info` | Informações detalhadas de snapshot/pacote |
| `export` | Exportar snapshot para arquivo .tar.gz |
| `import` | Importar snapshot de arquivo .tar.gz |
| `cleanup` | Remover snapshots antigos |
| `shell` | Modo shell interativo |

## Configuração

O ProteusOS usa um arquivo de configuração em `~/.proteusrc`:

```json
{
  "base_dir": "/home/user/proteus_os",
  "default_image": "alpine",
  "verbose": false,
  "auto_rollback": true
}
```

## Compilando o Módulo C

Se você quiser compilar o módulo C manualmente:

```bash
# Compilar o módulo C
python3 setup.py build_ext --inplace

# Testar
python3 -c "import snapshot; print(snapshot.build('teste'))"
```

## Testes

O projeto inclui testes automatizados:
```bash
# Executar todos os testes
python3 -m unittest tests/test_proteus.py -v

# Executar um teste específico
python3 -m unittest tests/test_proteus.py.TestProteusOS.test_build_snapshot -v
```

## Logs

O ProteusOS mantém logs estruturados em:
- **Console**: Saída colorida com níveis de log
- **Arquivo**: `~/proteus_os/proteusos_YYYYMMDD.log`

Os logs incluem:
- Timestamp, nível e mensagem
- Sanitização automática de dados sensíveis
- Rastreamento de operações críticas

## Desenvolvimento

### Adicionar novos comandos
1. Crie o comando no `cli.py`
2. Adicione ao parser do `argparse`
3. Implemente o método `_cmd_*`
4. Adicione ao shell (`shell.py`) se aplicável

### Adicionar novas funções em C
1. Edite `src/c_bridge/snapshot.c`
2. Adicione a função em C
3. Registre no `PyMethodDef`
4. Compile com `python3 setup.py build_ext --inplace`
5. Importe e use no Python

### Adicionar novas funcionalidades
- **Novos tipos de snapshot**: Modifique `builder.py`
- **Novos formatos de pacote**: Modifique `pkg_manager.py`
- **Novos métodos de atualização**: Modifique `updater.py`
- **Novos drivers de pacote**: Modifique `drivers.py`
- **Novos serviços**: Modifique `init_manager.py`
- **Melhorias na ISO**: Modifique `distro_builder.py`

## Segurança

O ProteusOS implementa várias camadas de segurança:

- **Sanitização de entrada**: Previne path traversal e injeção
- **Checksum SHA-256**: Verifica integridade de snapshots
- **File locking**: Previne corrupção em operações concorrentes
- **Log sanitization**: Remove informações sensíveis dos logs
- **Backup automático**: Recupera metadados corrompidos
- **Validação de dependências**: Verifica pacotes antes da instalação
- **Rollback automático**: Reverte instalações com falha

## Próximos Passos (Migração para C)

- Sistema de Arquivos: Implementar em C com chamadas de sistema
- Gerenciamento de Memória: Controle manual de alocação
- Threads e Sincronização: Paralelismo com pthreads
- Bootloader: Inicialização do sistema
- Kernel: Funcionalidades básicas de kernel
- **ISO Builder**: Migrar para C para melhor performance

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## Licença

MIT License 2024

Mantido por Jhonatan L. Santos (https://github.com/ojhonatanls)
