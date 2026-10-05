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