# ProteusOS - Sistema Operacional Minimalista e Modular

## Visão Geral

ProteusOS é um sistema operacional minimalista que implementa conceitos de:

- Imagens Atômicas: Cada atualização gera um snapshot completo do sistema
- Rollback Imediato: Reversão para estados anteriores em caso de falha
- Gerenciamento Transacional: Atualizações aplicadas de forma atômica
- Arquitetura Modular: Componentes independentes e substituíveis

## Requisitos

- Python 3.10+
- Biblioteca padrão (sem dependências externas)

## Instalação

Clone ou crie a estrutura do projeto:
mkdir -p ~/proteus_os
cd ~/proteus_os

Copie todos os arquivos da pasta src/ e o script proteus.
Torne o script executável:
chmod +x proteus

## Uso

Construir um sistema base:
./proteus build --base-image alpine
./proteus build --base-image debian

Status do sistema:
./proteus status

Aplicar uma atualização:
./proteus update /path/to/update

Rollback:
./proteus rollback
Para um snapshot específico:
./proteus rollback --snapshot-id snapshot_20240101_120000_alpine

Gerenciar pacotes:
Instalar um pacote:
./proteus package install /path/to/package

Listar pacotes instalados:
./proteus package list

Desinstalar um pacote:
./proteus package uninstall package_id

## Arquitetura

SystemBuilder (builder.py):
Gerencia a criação e versionamento de snapshots. Cada snapshot é uma imagem completa do sistema armazenada como tar.gz.

PackageManager (pkg_manager.py):
Gerencia pacotes de forma transacional, permitindo instalação e desinstalação com rollback.

SystemUpdater (updater.py):
Gerencia atualizações do sistema com garantias de atomicidade e rollback automático.

CLI (cli.py):
Interface de linha de comando que expõe todas as funcionalidades.

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