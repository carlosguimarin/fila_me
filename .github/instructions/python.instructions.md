---
applyTo: "**/*.py"
---

# Instruções Python — Fila ME

- Preserve a arquitetura existente antes de propor refatoração.
- Não mover regra de negócio da fila para a UI.
- Banco é responsável pela decisão centralizada de atribuição.
- Não usar estado local para decidir o próximo técnico.
- Ao alterar `banco.py`, verificar `docs/regras_negocio.md` e `docs/banco_dados.md`.
- Ao alterar autenticação, verificar `docs/seguranca.md`.
- Manter código simples e legível.
- Não adicionar dependências sem necessidade.
- Não imprimir segredos.
