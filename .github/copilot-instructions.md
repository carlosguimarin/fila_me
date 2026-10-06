# Fila ME — Contexto para GitHub Copilot

O repositório contém uma aplicação Python/Tkinter desktop chamada Fila ME, uma extensão de navegador para leitura do dashboard OTRS e persistência central em PostgreSQL/Neon.

Antes de alterações relevantes, consulte o documento específico em `docs/`.

## Regras funcionais que não podem ser quebradas

- Somente técnicos ativos e marcados como `trabalhando=true` participam da fila.
- Supervisores nunca entram automaticamente na fila.
- A atribuição inicial de um ticket avança a fila.
- O Owner posterior do OTRS serve para confirmação/auditoria e NÃO corrige a fila.
- Outro técnico que assumir um ticket fora da vez não altera `fila_estado`.
- Supervisor que assumir um ticket não altera `fila_estado`.
- Owner desconhecido não deve ser automaticamente classificado como supervisor.
- Número do ticket é único e deve impedir reprocessamento como novo.
- A seleção/avanço da fila precisa ser centralizada no Neon e protegida contra concorrência.

## Segurança

- Nunca incluir `.env`, `DATABASE_URL` ou senhas no código/repositório.
- Não expor credenciais em logs.
- Não alterar autenticação sem considerar PBKDF2-HMAC-SHA256 já adotado.

## Validação

Após mudanças:
1. executar testes existentes;
2. executar o aplicativo;
3. testar o fluxo afetado;
4. verificar o diff;
5. atualizar documentação se comportamento ou arquitetura mudar.

Para detalhes, consulte `AGENTS.md` e `docs/AI_CONTEXT.md`.
