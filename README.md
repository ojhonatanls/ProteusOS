# ProteusOS - Sistema Operacional Minimalista e Modular

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/ojhonatanls/ProteusOS/releases/tag/v1.0.0)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-4%20passing-brightgreen.svg)](https://github.com/ojhonatanls/ProteusOS/actions)

## Visão Geral

ProteusOS é um sistema operacional minimalista que implementa conceitos de:

- **Imagens Atômicas**: Cada atualização gera um snapshot completo do sistema
- **Rollback Imediato**: Reversão para estados anteriores em caso de falha
- **Gerenciamento Transacional**: Atualizações aplicadas de forma atômica
- **Arquitetura Modular**: Componentes independentes e substituíveis

## Status do Projeto

-  Sistema de build funcionando
-  Gerenciamento de snapshots
-  Gerenciamento de pacotes com dependências
-  Sistema de atualizações atômicas
-  Rollback para qualquer snapshot
-  CLI completa e funcional
-  Modo shell interativo
-  Gerenciador de configuração
-  Testes automatizados
-  Comando info para detalhes

## Requisitos

- Python 3.10+
- Biblioteca padrão (sem dependências externas)

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
│   ├── builder.py          # Gerenciador de snapshots
│   ├── pkg_manager.py      # Gerenciador de pacotes com dependências
│   ├── updater.py          # Gerenciador de atualizações
│   ├── config.py           # Gerenciador de configuração
│   └── shell.py            # Modo shell interativo
├── tests/                  # Testes automatizados
│   └── test_proteus.py     # Suite de testes
├── update_example/         # Exemplo de pacote de atualização
└── README.md               # Documentação
```

## Uso

### Modo CLI (Tradicional)
```bash
# Construir um sistema base
./proteus build --base-image alpine
./proteus build --base-image debian

# Status do sistema
./proteus status

# Aplicar uma atualização
./proteus update /path/to/update

# Rollback
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
```

### Modo Shell Interativo
```bash
# Entrar no shell
./proteus shell

# Dentro do shell, usar comandos diretamente
proteus> status
proteus> build --base-image alpine
proteus> package list
proteus> info pkg_20260820_094901
proteus> config --show
proteus> exit
```

### Comandos do Shell
| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `build` | Construir sistema base | `build --base-image alpine` |
| `status` | Ver status do sistema | `status` |
| `update` | Aplicar atualização | `update /path/to/update` |
| `rollback` | Rollback para snapshot | `rollback snapshot_ID` |
| `package` | Gerenciar pacotes | `package install pacote.tar.gz` |
| `config` | Gerenciar configurações | `config --show` |
| `info` | Informações detalhadas | `info snapshot_ID` |
| `clear` | Limpar tela | `clear` |
| `help` | Mostrar ajuda | `help` |
| `exit`/`quit` | Sair do shell | `exit` |

## Exemplos Práticos

### 1. Criar um sistema Alpine
```bash
./proteus build --base-image alpine
```

### 2. Verificar snapshots disponíveis
```bash
./proteus status
```

### 3. Criar um pacote de exemplo com dependências
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

### 4. Instalar o pacote
```bash
./proteus package install meu_pacote.tar.gz
```

### 5. Listar pacotes instalados
```bash
./proteus package list
```

### 6. Criar e aplicar uma atualização
```bash
mkdir -p minha_atualizacao
echo 'echo "Atualização aplicada com sucesso!"' > minha_atualizacao/update.sh
chmod +x minha_atualizacao/update.sh
echo '{"version": "1.1", "changelog": "Primeira atualização"}' > minha_atualizacao/metadata.json
tar -czf minha_atualizacao.tar.gz -C minha_atualizacao .
./proteus update minha_atualizacao.tar.gz
```

### 7. Rollback para um snapshot anterior
```bash
./proteus rollback --snapshot-id snapshot_20260820_094557_alpine
```

### 8. Usar o shell interativo
```bash
./proteus shell
proteus> status
proteus> build --base-image debian
proteus> package list
proteus> exit
```

### 9. Ver informações detalhadas
```bash
# Informações de um snapshot
./proteus info snapshot_20260820_100752_alpine

# Informações de um pacote
./proteus info pkg_20260820_094901
```

### 10. Gerenciar configurações
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
Gerencia a criação e versionamento de snapshots. Cada snapshot é uma imagem completa do sistema armazenada como tar.gz.

**PackageManager (pkg_manager.py)**
Gerencia pacotes de forma transacional, permitindo instalação e desinstalação com rollback. Suporta dependências entre pacotes.

**SystemUpdater (updater.py)**
Gerencia atualizações do sistema com garantias de atomicidade e rollback automático.

**CLI (cli.py)**
Interface de linha de comando que expõe todas as funcionalidades, incluindo configuração e informações detalhadas.

**Config (config.py)**
Gerenciador de configuração centralizado com suporte a arquivo `~/.proteusrc`.

**Shell (shell.py)**
Modo interativo para executar comandos do ProteusOS em um ambiente shell persistente.

## Comandos Disponíveis

| Comando | Descrição |
|---------|-----------|
| `build` | Construir um sistema base (alpine/debian) |
| `status` | Status do sistema e snapshots |
| `update` | Aplicar uma atualização |
| `rollback` | Rollback para um snapshot |
| `package` | Gerenciar pacotes (install/list/uninstall) |
| `config` | Gerenciar configurações (--show/--set) |
| `info` | Informações detalhadas de snapshot/pacote |
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

## Testes

O projeto inclui testes automatizados:
```bash
# Executar todos os testes
python3 -m unittest tests/test_proteus.py -v

# Executar um teste específico
python3 -m unittest tests/test_proteus.py.TestProteusOS.test_build_snapshot -v
```

## Desenvolvimento

### Adicionar novos comandos
1. Crie o comando no `cli.py`
2. Adicione ao parser do `argparse`
3. Implemente o método `_cmd_*`
4. Adicione ao shell (`shell.py`) se aplicável

### Adicionar novas funcionalidades
- **Novos tipos de snapshot**: Modifique `builder.py`
- **Novos formatos de pacote**: Modifique `pkg_manager.py`
- **Novos métodos de atualização**: Modifique `updater.py`

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
