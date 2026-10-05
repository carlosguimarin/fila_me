# Fila ME — Arquitetura

## 1. Visão geral

O sistema possui três partes principais:

```text
┌─────────────────────────┐
│        OTRS              │
│ Dashboard de tickets     │
└────────────┬────────────┘
             │ DOM
             ▼
┌─────────────────────────┐
│ Extensão Edge/Chrome     │
│ lê Ticket + Owner        │
└────────────┬────────────┘
             │ HTTP localhost
             ▼
┌─────────────────────────┐
│ Fila ME local            │
│ Python + Tkinter         │
│ servidor local           │
└────────────┬────────────┘
             │ SQL
             ▼
┌─────────────────────────┐
│ Neon PostgreSQL          │
│ estado compartilhado     │
└─────────────────────────┘
```

Cada computador possui uma instância local do Fila ME, mas todos apontam para o mesmo banco central.

## 2. Por que o banco é central

Se cada computador mantivesse sua própria fila, Carlos poderia acreditar que o próximo é Luís enquanto o computador de Luís acredita que o próximo é Daniel.

O Neon é a autoridade para:
- tickets conhecidos;
- usuários;
- quem está trabalhando;
- último técnico da fila;
- atribuições.

## 3. Concorrência

Dois computadores podem detectar o mesmo ticket praticamente ao mesmo tempo.

A proteção ocorre em camadas:

1. ticket único;
2. `INSERT ... ON CONFLICT DO NOTHING`;
3. se o ticket já existe, não criar nova atribuição;
4. bloqueio da linha de `fila_estado` com `FOR UPDATE`;
5. seleção e avanço dentro da transação.

## 4. Componentes Python conhecidos

### `app.py`

Responsável pelo ciclo principal da aplicação:
- criar root Tkinter;
- iniciar servidor local;
- mostrar login;
- abrir tela principal;
- voltar ao login;
- encerrar aplicação.

### `database/banco.py`

Centraliza acesso ao banco.

Funções conhecidas:
- `conectar`
- `criar_tabelas`
- `registrar_ticket`
- `buscar_tecnicos_trabalhando`
- `registrar_ticket_e_atribuir`
- `buscar_ultimas_atribuicoes`
- `buscar_proximo_tecnico`
- `criar_usuario`
- `buscar_usuario_por_email`
- `atualizar_status_trabalhando`
- `atualizar_atribuicao_owner`

### `database/autenticacao.py`

Responsável por:
- gerar hash;
- verificar senha;
- cadastrar usuário;
- autenticar usuário.

### `janela_principal.py`

Responsável por:
- UI principal;
- estado `trabalhando`;
- indicação do próximo;
- histórico;
- botão Sair;
- botão Fixar.

## 5. Autenticação

O formato utilizado é:

```text
PBKDF2-HMAC-SHA256
salt aleatório de 16 bytes
600.000 iterações
```

O hash é armazenado em formato que permite reconstruir os parâmetros necessários para verificação.

## 6. Servidor local

A extensão não deve acessar diretamente o banco.

Ela envia dados para:

```text
127.0.0.1:8765
```

O Python recebe e faz a persistência/decisão.

Isso reduz a exposição do banco ao navegador e mantém a regra de negócio no backend local + banco central.

## 7. UI

A interface usa Tkinter.

A janela pode ser colocada acima das demais com:

```python
root.attributes("-topmost", True)
```

O estado visual do botão muda entre:
- `📌 Fixar`
- `📌 Fixado`

## 8. Atualização

A tela principal consulta o estado periodicamente, atualmente em intervalo de aproximadamente 5 segundos.

A extensão também faz polling em aproximadamente 5 segundos.

## 9. Princípio arquitetural importante

A extensão detecta fatos do OTRS.

Ela NÃO deve decidir:
- quem é o próximo técnico;
- se supervisor entra na fila;
- como corrigir a fila.

Essas regras pertencem à aplicação/banco.
