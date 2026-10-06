# Fila ME — Banco de Dados

## 1. Banco

PostgreSQL hospedado no Neon.

Projeto conhecido:

```text
fila-me
```

Região mencionada durante configuração:
AWS South America East 1 — São Paulo.

A string de conexão não deve ser documentada.

## 2. Tabelas

### `tickets`

Estrutura conhecida:

```sql
tickets(
    numero_ticket BIGINT PRIMARY KEY,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

Função:
- catálogo de tickets já registrados;
- impede duplicação por número.

### `fila_estado`

Estrutura funcional:

```sql
fila_estado(
    id INTEGER PRIMARY KEY,
    indice_atual INTEGER NOT NULL,
    ultimo_tecnico_id BIGINT
)
```

A linha utilizada pela fila é:

```text
id = 1
```

O campo crítico para a regra atual é:

```text
ultimo_tecnico_id
```

A posição não deve ser recalculada a partir do Owner posterior do OTRS.

### `atribuicoes`

Estrutura conhecida:

```sql
atribuicoes(
    id BIGSERIAL PRIMARY KEY,
    numero_ticket BIGINT UNIQUE REFERENCES tickets,
    tecnico VARCHAR(150),
    atribuido_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(30) NOT NULL DEFAULT 'PENDENTE',
    owner_otrs VARCHAR(150),
    confirmado_em TIMESTAMP,
    tipo_atribuicao VARCHAR(30) NOT NULL DEFAULT 'TECNICO'
)
```

`tecnico` pode ser NULL.

Estados usados:
- `PENDENTE`
- `CONFIRMADO`
- `AGUARDANDO_TECNICO`

Tipos conhecidos:
- `TECNICO`
- `SUPERVISAO`

### `usuarios`

Estrutura conhecida:

```sql
usuarios(
    id BIGSERIAL PRIMARY KEY,
    nome VARCHAR(150),
    email VARCHAR(255) UNIQUE,
    senha_hash TEXT,
    cargo CHECK ('tecnico' ou 'supervisao'),
    ativo BOOLEAN DEFAULT TRUE,
    trabalhando BOOLEAN DEFAULT FALSE,
    criado_em TIMESTAMP
)
```

## 3. Fluxo transacional de novo ticket

Conceitualmente:

```text
BEGIN

INSERT ticket
ON CONFLICT DO NOTHING

se já existia:
    não criar atribuição
    finalizar

buscar técnicos:
    cargo = tecnico
    ativo = true
    trabalhando = true

se nenhum:
    criar atribuição AGUARDANDO_TECNICO
    COMMIT

se existem:
    SELECT fila_estado ... FOR UPDATE

    descobrir próximo técnico elegível
    inserir atribuição PENDENTE
    atualizar ultimo_tecnico_id

COMMIT
```

## 4. Por que `FOR UPDATE`

Sem bloqueio, dois computadores poderiam fazer:

```text
PC Carlos: lê "último = Carlos"
PC Luís:   lê "último = Carlos"

ambos escolhem Luís
```

Com o bloqueio, uma transação entra primeiro, atualiza o estado e a próxima lê o novo estado.

## 5. Atualização pelo Owner

`atualizar_atribuicao_owner`:
- bloqueia a atribuição;
- procura usuário ativo por nome, sem diferenciar maiúsculas/minúsculas;
- trata supervisor;
- trata técnico igual ao provisional;
- trata técnico diferente;
- trata Owner desconhecido.

Nenhum desses caminhos deve alterar a posição da fila.

## 6. Reset de desenvolvimento

Reset oficial preservando usuários:

```sql
TRUNCATE TABLE
    atribuicoes,
    tickets
RESTART IDENTITY CASCADE;

UPDATE fila_estado
SET
    indice_atual = 0,
    ultimo_tecnico_id = NULL
WHERE id = 1;

UPDATE usuarios
SET trabalhando = FALSE;
```

Reset total, incluindo usuários:

```sql
TRUNCATE TABLE
    atribuicoes,
    tickets,
    usuarios
RESTART IDENTITY CASCADE;

UPDATE fila_estado
SET
    indice_atual = 0,
    ultimo_tecnico_id = NULL
WHERE id = 1;
```

O reset total é somente para desenvolvimento/testes.

## 7. Atenção

Nunca executar reset em banco de produção sem uma decisão explícita.

Não colocar comandos de reset em fluxo automático da aplicação.
