# Estado Atual do Fila ME

> Documento de acompanhamento. Atualizar sempre que uma funcionalidade importante mudar.

## 1. Stack conhecida

- Python
- Tkinter para interface desktop
- PostgreSQL
- Neon como banco central
- extensão de navegador em JavaScript
- comunicação da extensão com servidor local Python via `127.0.0.1:8765`
- OTRS como sistema de tickets
- PyInstaller para gerar executável

## 2. Componentes conhecidos

Estrutura relevante:

```text
src/fila_me/
├── app.py
├── database/
│   ├── banco.py
│   └── autenticacao.py
├── ...
```

Também existem:
- `docs/`
- `tests/`
- arquivos da extensão do navegador
- `requirements.txt`

A estrutura exata deve ser confirmada na branch antes de criar novos caminhos.

## 3. Funcionalidades confirmadas durante desenvolvimento

### Autenticação

- Login por e-mail e senha.
- Cadastro de usuário.
- Cargo:
  - Técnico
  - Supervisão
- Usuário pode estar ativo/inativo.
- Técnico possui estado de trabalho (`trabalhando`).

### Tela principal

- Nome do usuário no cabeçalho.
- Cargo exibido.
- Botão `Sair`.
- Botão `📌 Fixar` / `📌 Fixado`.
- Indicador `Próximo`.
- Histórico das últimas atribuições.
- Atualização periódica do estado.
- Técnico entra como trabalhando ao abrir a tela.
- Técnico sai da fila ao fazer logout/encerrar.

### Fila

- Estado centralizado no Neon.
- Somente técnicos ativos com `trabalhando = TRUE` e heartbeat válido por 15 segundos participam.
- Atribuição inicial avança a fila.
- Owner posterior não corrige a posição da fila.
- Uma atribuição existente em `AGUARDANDO_TECNICO` pode ser reavaliada quando o ticket volta a ser recebido pela integração. O Owner é processado primeiro; Supervisão não entra na fila técnica.

### OTRS

- Extensão lê o dashboard.
- Número do ticket, `PROPRIETÁRIO` e `BLOQUEAR` são enviados em campos separados; o bloqueio tem coluna própria no banco e não substitui o Owner.
- Polling atual: aproximadamente 5 segundos.
- A aplicação local recebe os dados.
- O estado atual de bloqueio fica em `tickets.status_bloqueio`; o primeiro bloqueio explícito também fica confirmado permanentemente, mesmo após leituras de `desbloqueado`.

### Histórico

A tela foi ajustada para exibir:
- nome do técnico quando aplicável;
- `Supervisão` quando a atribuição foi reconhecida como supervisão;
- `Aguardando técnico` quando não havia técnico trabalhando.

## 4. Build

Foi gerado e testado um executável com PyInstaller:

```text
dist/FilaME.exe
```

O executável utiliza um `.env` ao lado dele quando congelado.

Importante: alterações posteriores ao build tornam o `.exe` potencialmente desatualizado. Não considerar o executável como equivalente automático ao código-fonte.

## 5. Pendências/conferências

Antes de uma release final, conferir:
- todos os commits da branch `carlos` foram integrados;
- branch `luis` está sincronizada;
- documentação foi commitada;
- testes automatizados existem e estão atualizados;
- testes manuais críticos foram repetidos;
- `main` recebeu somente o que foi aprovado;
- executável foi reconstruído após o último código aprovado;
- extensão distribuída corresponde ao código aprovado.

A sintaxe do fluxo recente de reavaliação foi conferida, mas sua operação com Neon/OTRS e o ciclo completo ainda precisam ser validados antes de distribuir o executável.

## 6. Integração da V2 de interface

Antes de integrar uma mudança grande de UI, seguir `integracao_v2.md`. A UI pode mudar de organização e aparência, mas deve preservar os contratos de banco, fila, presença, Owner, Supervisão, servidor local e encerramento descritos nos documentos de regras e arquitetura.

### Integração visual na branch `luis` (2026-10-14)

A interface Tkinter da V2 foi adaptada para a V1: temas claro/escuro, modo simples/avançado, cores, filtro visual, lista rolável, indicador de técnicos elegíveis, menus e ícones locais. As preferências são locais por usuário. A tela usa `buscar_painel_visual()` apenas para leitura e mantém login/cadastro da V1 por e-mail, assim como o heartbeat técnico de 5 segundos, a validade de 15 segundos e a limpeza no encerramento.

Não foram integrados o identificador OTRS, as sessões/heartbeat de 90 segundos, a leitura de Owner da extensão V2 nem o servidor V2. A leitura V1 extrai `PROPRIETÁRIO` e `BLOQUEAR` por cabeçalho e envia os valores em campos separados. `tickets.status_bloqueio` guarda o estado atual; `bloqueio_confirmado` persiste o primeiro bloqueio e colore a barra de verde. A lista online mostra técnicos elegíveis da V1; a V1 não rastreia presença de Supervisão.

O código V1 de `atualizar_atribuicao_owner()` atualmente substitui `atribuicoes.tecnico` pelo nome de outro técnico que assume o chamado. Isso difere da descrição documental de `tecnico` como atribuição provisória permanente. Por decisão do responsável, a integração visual mantém o comportamento funcional da V1; a tela evita rotular esse valor como “inicial”. Uma eventual mudança nessa persistência exigiria análise própria de regra e migração, fora da integração visual.

O executável ainda precisa ser reconstruído e validado com Neon/OTRS no ambiente operacional. O `FilaME.spec` foi adaptado para incluir os ícones no bundle; `.env` continua externo ao ZIP.
