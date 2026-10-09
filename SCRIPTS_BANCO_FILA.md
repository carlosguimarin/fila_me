# FILA ME — Scripts rápidos do banco (Neon PostgreSQL)

> Use este arquivo como referência operacional. Execute os SELECTs antes de qualquer UPDATE/DELETE.
>
> **Atenção:** `atribuicoes.tecnico` é a atribuição feita pelo FILA; `atribuicoes.owner_otrs` é o Owner observado no OTRS. Não são a mesma coisa.
>
> **Não execute DELETE em `tickets`** para corrigir uma atribuição errada, salvo se houver um motivo específico confirmado. O registro em `tickets` impede que o mesmo número seja tratado como novo novamente.

---

## 1. Consultar IDs dos usuários

```sql
SELECT id, nome, cargo, ativo, trabalhando, ultimo_heartbeat
FROM usuarios
ORDER BY id;
```

IDs conhecidos no histórico (confirme sempre com o SELECT acima):

- `2` — Daniel Bopp de Sá
- `3` — Carlos Guilherme Marin
- `4` — Luís Bolina Martins

Os IDs normalmente permanecem estáveis enquanto os registros dos usuários não forem excluídos/recriados.

## 2. Ver quem está trabalhando / heartbeat

```sql
SELECT id, nome, ativo, trabalhando, ultimo_heartbeat
FROM usuarios
WHERE cargo = 'tecnico'
ORDER BY id;
```

Com heartbeat, o esperado é que `ultimo_heartbeat` seja atualizado periodicamente. Alterar `trabalhando = FALSE` manualmente não é permanente se o aplicativo do técnico continuar aberto e enviando heartbeat.

## 3. Consultar o estado atual da fila

```sql
SELECT *
FROM fila_estado
WHERE id = 1;
```

Campo mais importante:

- `ultimo_tecnico_id`: ID do último técnico que consumiu a vez. O próximo é calculado a partir dos técnicos elegíveis e desse ID.

## 4. Ver o próximo técnico (consulta manual)

Esta consulta calcula o próximo técnico usando os usuários marcados como ativos e trabalhando. Se o projeto estiver usando heartbeat na função Python, acrescente a condição de validade do heartbeat para reproduzir exatamente a lógica do app.

```sql
WITH tecnicos AS (
    SELECT id, nome,
           ROW_NUMBER() OVER (ORDER BY id) AS posicao
    FROM usuarios
    WHERE cargo = 'tecnico'
      AND ativo = TRUE
      AND trabalhando = TRUE
),
ultimo AS (
    SELECT ultimo_tecnico_id
    FROM fila_estado
    WHERE id = 1
),
ultimo_pos AS (
    SELECT t.posicao
    FROM tecnicos t
    CROSS JOIN ultimo u
    WHERE t.id = u.ultimo_tecnico_id
)
SELECT t.id, t.nome
FROM tecnicos t
CROSS JOIN ultimo u
LEFT JOIN ultimo_pos up ON TRUE
WHERE
    u.ultimo_tecnico_id IS NULL
    OR (up.posicao IS NULL AND t.posicao = 1)
    OR (
        up.posicao IS NOT NULL
        AND t.posicao = (
            SELECT CASE
                WHEN MAX(posicao) = up.posicao THEN 1
                ELSE up.posicao + 1
            END
            FROM tecnicos
        )
    );
```

> Esta consulta é para conferência manual. A lógica Python do app é a referência final, especialmente quando heartbeat estiver integrado.

## 5. Consultar um chamado específico

Troque o número do ticket:

```sql
SELECT
    a.numero_ticket,
    a.tecnico,
    a.owner_otrs,
    a.status,
    a.tipo_atribuicao,
    a.ultimo_tecnico_id_anterior,
    a.atribuido_em,
    a.confirmado_em
FROM atribuicoes a
WHERE a.numero_ticket = 2026100954000306;
```

## 6. Consultar chamado + estado atual da fila

Use antes de corrigir um chamado que avançou a fila:

```sql
SELECT
    a.numero_ticket,
    a.tecnico,
    a.owner_otrs,
    a.status,
    a.tipo_atribuicao,
    a.ultimo_tecnico_id_anterior,
    f.ultimo_tecnico_id AS ultimo_tecnico_atual
FROM atribuicoes a
CROSS JOIN fila_estado f
WHERE a.numero_ticket = 2026100954000306
  AND f.id = 1;
```

## 7. Ver últimas atribuições

```sql
SELECT
    id,
    numero_ticket,
    tecnico,
    owner_otrs,
    status,
    tipo_atribuicao,
    ultimo_tecnico_id_anterior,
    atribuido_em
FROM atribuicoes
ORDER BY id DESC
LIMIT 20;
```

## 8. Remover uma atribuição errada e restaurar a fila

**Só use este padrão quando confirmou que o chamado é o avanço que deseja desfazer e que não ocorreram atribuições válidas posteriores que devam ser preservadas.**

Primeiro execute o SELECT da seção 6 e confira `ultimo_tecnico_id_anterior`.

Depois substitua:
- `TICKET_ERRADO` pelo número do chamado;
- `ID_ANTERIOR` pelo valor confirmado em `ultimo_tecnico_id_anterior`.

```sql
BEGIN;

SELECT numero_ticket, tecnico, status, tipo_atribuicao,
       ultimo_tecnico_id_anterior
FROM atribuicoes
WHERE numero_ticket = TICKET_ERRADO
FOR UPDATE;

DELETE FROM atribuicoes
WHERE numero_ticket = TICKET_ERRADO;

UPDATE fila_estado
SET ultimo_tecnico_id = ID_ANTERIOR
WHERE id = 1;

COMMIT;
```

**Não copie o SQL acima literalmente:** `TICKET_ERRADO` e `ID_ANTERIOR` são marcadores que precisam ser substituídos por números reais. Não use o `ultimo_tecnico_id_anterior` sem verificar se houve outros avanços depois.

## 9. Ajustar manualmente o último técnico da fila

Use apenas quando souber qual técnico deve ser considerado o último a consumir a vez. O próximo será calculado a partir dele.

Exemplo para registrar o Luís (ID 4) como último:

```sql
BEGIN;

UPDATE fila_estado
SET ultimo_tecnico_id = 4
WHERE id = 1;

SELECT *
FROM fila_estado
WHERE id = 1;

COMMIT;
```

IDs conhecidos no histórico: Daniel `2`, Carlos `3`, Luís `4`. Confirme na tabela `usuarios` antes de executar.

## 10. Ver se um ticket já foi registrado

```sql
SELECT numero_ticket, criado_em
FROM tickets
WHERE numero_ticket = 2026100954000306;
```

## 11. Remover usuário temporariamente da fila — cuidado

Não use apenas este comando se o app do usuário continuar aberto e o heartbeat estiver ativo, porque o usuário pode voltar a `trabalhando = TRUE` em poucos segundos:

```sql
UPDATE usuarios
SET trabalhando = FALSE,
    ultimo_heartbeat = NULL
WHERE id = 4;
```

Também não desative `ativo` sem entender o impacto: isso pode impedir o login. O controle administrativo separado de disponibilidade/participação na fila ainda é uma melhoria pendente no histórico.

---

## Checklist antes de corrigir um ticket

1. Consultar o ticket na tabela `atribuicoes`.
2. Consultar `ultimo_tecnico_id_anterior`.
3. Consultar o `ultimo_tecnico_id` atual em `fila_estado`.
4. Verificar as atribuições criadas depois do ticket.
5. Confirmar que restaurar o estado anterior não desfaz uma atribuição válida posterior.
6. Só então executar a transação.
7. Consultar novamente `fila_estado` e as últimas atribuições.
