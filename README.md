
# ProteusOS - Sistema Operacional Minimalista e Modular

[![Version](https://img.shields.io/badge/version-2.0.1-blue.svg)](https://github.com/ojhonatanls/ProteusOS/releases/tag/v2.0.1)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-4%20passing-brightgreen.svg)](https://github.com/ojhonatanls/ProteusOS/actions)

## Visão Geral

ProteusOS é um sistema operacional minimalista que implementa conceitos de:

- **Imagens Atômicas**: Cada atualização gera um snapshot completo do sistema
- **Rollback Imediato**: Reversão para estados anteriores em caso de falha
- **Gerenciamento Transacional**: Atualizações aplicadas de forma atômica
- **Arquitetura Modular**: Componentes independentes e substituíveis
- **Suporte a C**: Módulos em C para operações de alta performance
- **Integridade Garantida**: Verificação de checksum SHA-256 para snapshots

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

## Requisitos

- Python 3.10+
- Biblioteca padrão (sem dependências externas)
- GCC (para compilar módulos C, opcional)

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

# Status do sistema
./proteus status

# Aplicar uma atualização
./proteus update /path/to/update

# Rollback (com verificação de integridade)
./proteus rollback
./proteus rollback --snapshot-id snapshot_20240101_120000_alpine

# Gerenciar pacotes
./proteus package install /path/to/package
./proteus package list
./proteus package uninstall package_id

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
| `status` | Ver status do sistema | `status` |
| `update` | Aplicar atualização | `update /path/to/update` |
| `rollback` | Rollback para snapshot | `rollback snapshot_ID` |
| `package` | Gerenciar pacotes | `package install pacote.tar.gz` |
| `config` | Gerenciar configurações | `config --show` |
| `info` | Informações detalhadas | `info snapshot_ID` |
| `export` | Exportar snapshot | `export snapshot_ID` |
| `import` | Importar snapshot | `import /path/to/file.tar.gz` |
| `cleanup` | Limpar snapshots antigos | `cleanup --keep 3` |
| `clear` | Limpar tela | `clear` |
| `help` | Mostrar ajuda | `help` |
| `exit`/`quit` | Sair do shell | `exit` |

## Exemplos Práticos

### 1. Criar um sistema Alpine (Python)
```bash
./proteus build --base-image alpine
```

### 2. Criar um sistema Alpine (C - mais rápido)
```bash
./proteus build --base-image alpine --use-c
```

### 3. Verificar snapshots disponíveis
```bash
./proteus status
```

### 4. Criar um pacote de exemplo com dependências
```bash
mkdir -p meu_pacote
echo '{
  "name": "hello-world",
  "version": "1.0",
  "dependencies": {
    "base": "1.0"
  }
}' > meu_pacote/package.json
echo 'echo "Hello from ProteusOS"' > meu_pacote/hello.sh
chmod +x meu_pacote/hello.sh
tar -czf meu_pacote.tar.gz -C meu_pacote .
```

### 5. Instalar o pacote
```bash
./proteus package install meu_pacote.tar.gz
```

### 6. Listar pacotes instalados
```bash
./proteus package list
```

### 7. Exportar um snapshot
```bash
# Exportar para o diretório padrão (~/proteus_exports/)
./proteus export snapshot_20260820_111526_alpine

# Exportar para um local específico
./proteus export snapshot_20260820_111526_alpine --output ~/backups/meu_snapshot.tar.gz
```

### 8. Importar um snapshot
```bash
./proteus import ~/proteus_exports/snapshot_20260820_111526_alpine.tar.gz
```

### 9. Limpar snapshots antigos
```bash
# Manter apenas os 3 mais recentes
./proteus cleanup --keep 3

# Remover um snapshot específico
./proteus cleanup --snapshot-id snapshot_20260820_111526_debian
```

### 10. Usar o shell interativo
```bash
./proteus shell
proteus> status
proteus> build --base-image debian --use-c
proteus> package list
proteus> export snapshot_20260820_111526_alpine
proteus> exit
```

### 11. Ver informações detalhadas
```bash
# Informações de um snapshot (com checksum)
./proteus info snapshot_20260820_100752_alpine

# Informações de um pacote
./proteus info pkg_20260820_094901
```

### 12. Gerenciar configurações
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
Gerencia a criação e versionamento de snapshots. Cada snapshot é uma imagem completa do sistema armazenada como tar.gz, com checksum SHA-256 para garantir integridade.

**PackageManager (pkg_manager.py)**
Gerencia pacotes de forma transacional, permitindo instalação e desinstalação com rollback. Suporta dependências entre pacotes.

**SystemUpdater (updater.py)**
Gerencia atualizações do sistema com garantias de atomicidade e rollback automático, com verificação de integridade.

**CLI (cli.py)**
Interface de linha de comando que expõe todas as funcionalidades, incluindo export/import e cleanup.

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

## Comandos Disponíveis

| Comando | Descrição |
|---------|-----------|
| `build` | Construir um sistema base (alpine/debian) |
| `build --use-c` | Construir usando C (experimental) |
| `status` | Status do sistema e snapshots |
| `update` | Aplicar uma atualização |
| `rollback` | Rollback para um snapshot |
| `package` | Gerenciar pacotes (install/list/uninstall) |
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

## Segurança

O ProteusOS implementa várias camadas de segurança:

- **Sanitização de entrada**: Previne path traversal e injeção
- **Checksum SHA-256**: Verifica integridade de snapshots
- **File locking**: Previne corrupção em operações concorrentes
- **Log sanitization**: Remove informações sensíveis dos logs
- **Backup automático**: Recupera metadados corrompidos
- **Validação de dependências**: Verifica pacotes antes da instalação

## Próximos Passos (Migração para C)

- Sistema de Arquivos: Implementar em C com chamadas de sistema
- Gerenciamento de Memória: Controle manual de alocação
- Threads e Sincronização: Paralelismo com pthreads
- Bootloader: Inicialização do sistema
- Kernel: Funcionalidades básicas de kernel

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## Licença

MIT License 2024

Mantido por Jhonatan L. Santos (https://github.com/ojhonatanls)
