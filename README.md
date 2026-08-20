PROTEUSOS - SISTEMA OPERACIONAL MINIMALISTA E MODULAR

Visão Geral
-----------
ProteusOS é um sistema operacional minimalista que implementa conceitos de:

- Imagens Atômicas: Cada atualização gera um snapshot completo do sistema
- Rollback Imediato: Reversão para estados anteriores em caso de falha
- Gerenciamento Transacional: Atualizações aplicadas de forma atômica
- Arquitetura Modular: Componentes independentes e substituíveis

Status do Projeto
-----------------
✅ Sistema de build funcionando
✅ Gerenciamento de snapshots
✅ Gerenciamento de pacotes
✅ Sistema de atualizações atômicas
✅ Rollback para qualquer snapshot
✅ CLI completa e funcional

Requisitos
----------
- Python 3.10+
- Biblioteca padrão (sem dependências externas)

Instalação
----------
Clone o repositório:
git clone https://github.com/ojhonatanls/ProteusOS.git
cd ProteusOS

Torne o script executável:
chmod +x proteus

Estrutura do Projeto
--------------------
ProteusOS/
├── proteus              # Script principal executável
├── src/                 # Código-fonte
│   ├── cli.py           # Interface de linha de comando
│   ├── builder.py       # Gerenciador de snapshots
│   ├── pkg_manager.py   # Gerenciador de pacotes
│   └── updater.py       # Gerenciador de atualizações
└── update_example/      # Exemplo de pacote de atualização

Uso
---
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

Exemplos Práticos
-----------------
1. Criar um sistema Alpine:
./proteus build --base-image alpine

2. Verificar snapshots disponíveis:
./proteus status

3. Criar um pacote de exemplo:
mkdir -p meu_pacote
echo '{"name": "hello-world", "version": "1.0"}' > meu_pacote/package.json
echo 'echo "Hello from ProteusOS"' > meu_pacote/hello.sh
chmod +x meu_pacote/hello.sh
tar -czf meu_pacote.tar.gz -C meu_pacote .

4. Instalar o pacote:
./proteus package install meu_pacote.tar.gz

5. Listar pacotes instalados:
./proteus package list

6. Criar e aplicar uma atualização:
mkdir -p minha_atualizacao
echo 'echo "Atualização aplicada com sucesso!"' > minha_atualizacao/update.sh
chmod +x minha_atualizacao/update.sh
echo '{"version": "1.1", "changelog": "Primeira atualização"}' > minha_atualizacao/metadata.json
tar -czf minha_atualizacao.tar.gz -C minha_atualizacao .
./proteus update minha_atualizacao.tar.gz

7. Rollback para um snapshot anterior:
./proteus rollback --snapshot-id snapshot_20260820_094557_alpine

Arquitetura
-----------
SystemBuilder (builder.py):
Gerencia a criação e versionamento de snapshots. Cada snapshot é uma imagem
completa do sistema armazenada como tar.gz.

PackageManager (pkg_manager.py):
Gerencia pacotes de forma transacional, permitindo instalação e desinstalação
com rollback.

SystemUpdater (updater.py):
Gerencia atualizações do sistema com garantias de atomicidade e rollback
automático.

CLI (cli.py):
Interface de linha de comando que expõe todas as funcionalidades.

Comandos Disponíveis
--------------------
build     - Construir um sistema base (alpine/debian)
status    - Status do sistema e snapshots
update    - Aplicar uma atualização
rollback  - Rollback para um snapshot
package   - Gerenciar pacotes (install/list/uninstall)

Próximos Passos (Migração para C)
---------------------------------
- Sistema de Arquivos: Implementar em C com chamadas de sistema
- Gerenciamento de Memória: Controle manual de alocação
- Threads e Sincronização: Paralelismo com pthreads
- Bootloader: Inicialização do sistema
- Kernel: Funcionalidades básicas de kernel

Contribuição
------------
1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

Licença
-------
MIT License 2024

Mantido por Jhonatan L. Santos (https://github.com/ojhonatanls)