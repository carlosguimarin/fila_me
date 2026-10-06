# Fila ME — Histórico Técnico Conhecido

## Fase 1 — Ideia inicial

O projeto começou como uma aplicação de fila para três integrantes:

```text
Carlos
Luís
Daniel
```

A ideia inicial incluía:
- botões Próximo/Anterior;
- nomes dos integrantes;
- janela sempre no topo;
- leitura dos tickets;
- detecção de ticket novo;
- persistência para saber se ticket já foi visto.

## Fase 2 — Banco

Foi usado inicialmente SQLite em testes.

Foi criado algo equivalente a:

```text
src/fila_me/database/
```

e um script de teste.

O banco SQLite local foi posteriormente retirado do fluxo principal.

O projeto evoluiu para PostgreSQL/Neon porque a fila precisava ser compartilhada entre máquinas.

## Fase 3 — Git

Foi criado o repositório:

```text
carlosguimarin/fila_me
```

Branches:
- main
- carlos
- luis

Foi configurada proteção da `main` e fluxo por PR.

## Fase 4 — Persistência de tickets

Foi criado o mecanismo central de tickets.

Commit conhecido:

```text
b4bb007
Adiciona persistência de tickets no Neon
```

## Fase 5 — Usuários

Foi introduzido:
- cadastro;
- login;
- cargos;
- ativo;
- trabalhando;
- hash seguro de senha.

## Fase 6 — Atribuição automática

A fila passou a usar:
- técnicos trabalhando;
- último técnico;
- próximo técnico;
- transação;
- bloqueio `FOR UPDATE`.

## Fase 7 — Owner do OTRS

A extensão passou a coletar:
- número;
- Owner.

Foi necessário definir a diferença entre:
- atribuição provisional;
- Owner real.

A regra final foi documentada em `regras_negocio.md`.

## Fase 8 — Supervisão

Foi necessário reconhecer supervisores registrados.

A interface passou a mostrar:

```text
→ Supervisão
```

quando apropriado.

## Fase 9 — Janela fixada

O botão de fixação foi restaurado após ter sido perdido durante uma alteração de UI.

## Fase 10 — Testes com usuários reais do fluxo

Foi observado que:
- logout retira técnico da fila;
- se somente Luís estiver trabalhando, vários tickets seguidos podem ir para Luís;
- isso é esperado.

## Fase 11 — Executável

Foi criado:

```text
dist/FilaME.exe
```

e testado.

O `.env` fica separado.

## Estado desta documentação

Este histórico é uma reconstrução fiel do desenvolvimento conhecido até 2026-10-05.

Ele deve ser complementado com novos commits e decisões.
