---
applyTo: "**/database/**/*.py,**/*.sql"
---

# Instruções de banco — Fila ME

- Não alterar a regra de fila sem atualizar `docs/regras_negocio.md`.
- `numero_ticket` é único.
- `fila_estado` é central e concorrente.
- O avanço da fila deve ser protegido transacionalmente.
- Usar bloqueio apropriado (`FOR UPDATE`) quando necessário.
- Owner posterior não modifica `fila_estado`.
- Supervisor não participa da rotação.
- Nunca incluir connection string ou senha em código/documentação.
- SQL destrutivo de reset é somente para desenvolvimento.
