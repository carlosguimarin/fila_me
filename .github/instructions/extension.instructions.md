---
applyTo: "**/*.{js,json}"
---

# Instruções da extensão — Fila ME

- A extensão coleta informações do dashboard OTRS.
- Não colocar regra de distribuição de fila na extensão.
- Número do ticket e Owner devem ser enviados ao backend local.
- O polling pode reenviar o mesmo ticket; o backend/banco precisa ser idempotente.
- Não adicionar credenciais do banco à extensão.
- Após mudanças, validar o carregamento em `edge://extensions` e o Console.
