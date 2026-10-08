import os
import sys
import psycopg
from dotenv import load_dotenv
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
        )
    )
ARQUIVO_ENV = os.path.join(
    BASE_DIR,
    ".env",
)
load_dotenv(ARQUIVO_ENV)
DATABASE_URL = os.getenv("DATABASE_URL")

def conectar():
    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL não encontrada no arquivo .env"
        )
    return psycopg.connect(
        DATABASE_URL
    )

def criar_tabelas():
    with conectar() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    numero_ticket BIGINT PRIMARY KEY,
                    criado_em TIMESTAMP
                        DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fila_estado (
                    id INTEGER PRIMARY KEY,
                    indice_atual INTEGER NOT NULL,
                    ultimo_tecnico_id BIGINT
                );
            """)
            cursor.execute("""
                INSERT INTO fila_estado (
                    id,
                    indice_atual,
                    ultimo_tecnico_id
                )
                VALUES (1, 0, NULL)
                ON CONFLICT (id) DO NOTHING;
            """)
            cursor.execute("""
                ALTER TABLE fila_estado
                ADD COLUMN IF NOT EXISTS
                ultimo_tecnico_id BIGINT;
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS atribuicoes (
                    id BIGSERIAL PRIMARY KEY,
                    numero_ticket BIGINT NOT NULL UNIQUE
                        REFERENCES tickets(numero_ticket),
                    tecnico VARCHAR(150),
                    atribuido_em TIMESTAMP
                        DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(30)
                        NOT NULL DEFAULT 'PENDENTE',
                    owner_otrs VARCHAR(150),
                    confirmado_em TIMESTAMP,
                    tipo_atribuicao VARCHAR(30)
                        NOT NULL DEFAULT 'TECNICO',
                    ultimo_tecnico_id_anterior BIGINT
                );
            """)
            cursor.execute("""
                ALTER TABLE atribuicoes
                ALTER COLUMN tecnico DROP NOT NULL;
            """)
            cursor.execute("""
                ALTER TABLE atribuicoes
                ADD COLUMN IF NOT EXISTS
                status VARCHAR(30)
                NOT NULL DEFAULT 'PENDENTE';
            """)
            cursor.execute("""
                ALTER TABLE atribuicoes
                ADD COLUMN IF NOT EXISTS
                owner_otrs VARCHAR(150);
            """)
            cursor.execute("""
                ALTER TABLE atribuicoes
                ADD COLUMN IF NOT EXISTS
                confirmado_em TIMESTAMP;
            """)
            cursor.execute("""
                ALTER TABLE atribuicoes
                ADD COLUMN IF NOT EXISTS
                tipo_atribuicao VARCHAR(30)
                NOT NULL DEFAULT 'TECNICO';
            """)
            cursor.execute("""
                ALTER TABLE atribuicoes
                ADD COLUMN IF NOT EXISTS
                ultimo_tecnico_id_anterior BIGINT;
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id BIGSERIAL PRIMARY KEY,
                    nome VARCHAR(150) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    senha_hash TEXT NOT NULL,
                    cargo VARCHAR(20) NOT NULL
                        CHECK (
                            cargo IN (
                                'tecnico',
                                'supervisao'
                            )
                        ),
                    ativo BOOLEAN NOT NULL DEFAULT TRUE,
                    trabalhando BOOLEAN NOT NULL DEFAULT FALSE,
                    criado_em TIMESTAMP NOT NULL
                        DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cursor.execute("""
                ALTER TABLE usuarios
                ADD COLUMN IF NOT EXISTS
                ultimo_heartbeat TIMESTAMP;
            """)
        conn.commit()

def criar_tabela_tickets():
    criar_tabelas()

def registrar_ticket(numero_ticket):
    with conectar() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tickets (
                    numero_ticket
                )
                VALUES (%s)
                ON CONFLICT (
                    numero_ticket
                ) DO NOTHING
                RETURNING numero_ticket;
                """,
                (
                    numero_ticket,
                ),
            )
            resultado = cursor.fetchone()
        conn.commit()
    return resultado is not None

def buscar_tecnicos_trabalhando():
    with conectar() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    nome
                FROM usuarios
                WHERE cargo = 'tecnico'
                  AND ativo = TRUE
                  AND trabalhando = TRUE
                ORDER BY id;
                """
            )
            return cursor.fetchall()

def registrar_ticket_e_atribuir(numero_ticket):
    with conectar() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tickets (
                    numero_ticket
                )
                VALUES (%s)
                ON CONFLICT (
                    numero_ticket
                ) DO NOTHING
                RETURNING numero_ticket;
                """,
                (
                    numero_ticket,
                ),
            )
            ticket_novo = cursor.fetchone()
            if ticket_novo is None:
                conn.commit()
                return None
            cursor.execute(
                """
                SELECT
                    id,
                    nome
                FROM usuarios
                WHERE cargo = 'tecnico'
                  AND ativo = TRUE
                  AND trabalhando = TRUE
                ORDER BY id;
                """
            )
            tecnicos = cursor.fetchall()
            if not tecnicos:
                cursor.execute(
                    """
                    INSERT INTO atribuicoes (
                        numero_ticket,
                        tecnico,
                        status,
                        tipo_atribuicao
                    )
                    VALUES (
                        %s,
                        NULL,
                        'AGUARDANDO_TECNICO',
                        'TECNICO'
                    );
                    """,
                    (
                        numero_ticket,
                    ),
                )
                conn.commit()
                return {
                    "numero_ticket": numero_ticket,
                    "tecnico": None,
                    "status": "AGUARDANDO_TECNICO",
                }
            cursor.execute(
                """
                SELECT
                    ultimo_tecnico_id
                FROM fila_estado
                WHERE id = 1
                FOR UPDATE;
                """
            )
            ultimo = cursor.fetchone()
            ultimo_tecnico_id = (
                ultimo[0]
                if ultimo
                else None
            )
            ultimo_tecnico_id_anterior = (
                ultimo_tecnico_id
            )
            tecnico_escolhido = None
            if ultimo_tecnico_id is None:
                tecnico_escolhido = tecnicos[0]
            else:
                for indice, tecnico in enumerate(
                    tecnicos
                ):
                    if tecnico[0] == ultimo_tecnico_id:
                        proximo_indice = (
                            indice + 1
                        ) % len(tecnicos)
                        tecnico_escolhido = (
                            tecnicos[
                                proximo_indice
                            ]
                        )
                        break
                if tecnico_escolhido is None:
                    tecnico_escolhido = tecnicos[0]
            tecnico_id = tecnico_escolhido[0]
            tecnico_nome = tecnico_escolhido[1]
            cursor.execute(
                """
                INSERT INTO atribuicoes (
                    numero_ticket,
                    tecnico,
                    status,
                    tipo_atribuicao,
                    ultimo_tecnico_id_anterior
                )
                VALUES (
                    %s,
                    %s,
                    'PENDENTE',
                    'TECNICO',
                    %s
                );
                """,
                (
                    numero_ticket,
                    tecnico_nome,
                    ultimo_tecnico_id_anterior,
                ),
            )
            cursor.execute(
                """
                UPDATE fila_estado
                SET
                    ultimo_tecnico_id = %s
                WHERE id = 1;
                """,
                (
                    tecnico_id,
                ),
            )
        conn.commit()
    return {
        "numero_ticket": numero_ticket,
        "tecnico": tecnico_nome,
        "status": "PENDENTE",
    }

def buscar_ultimas_atribuicoes(limite=9):
    with conectar() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    numero_ticket,
                    CASE
                        WHEN tipo_atribuicao = 'SUPERVISAO'
                            THEN 'Supervisão'
                        WHEN tecnico IS NULL
                            THEN 'Aguardando técnico'
                        ELSE tecnico
                    END AS tecnico,
                    atribuido_em
                FROM atribuicoes
                ORDER BY id DESC
                LIMIT %s;
                """,
                (
                    limite,
                ),
            )
            return cursor.fetchall()

def buscar_proximo_tecnico():
    tecnicos = buscar_tecnicos_trabalhando()
    if not tecnicos:
        return "Nenhum técnico"
    with conectar() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    ultimo_tecnico_id
                FROM fila_estado
                WHERE id = 1;
                """
            )
            resultado = cursor.fetchone()
    ultimo_id = (
        resultado[0]
        if resultado
        else None
    )
    if ultimo_id is None:
        return tecnicos[0][1]
    for indice, tecnico in enumerate(
        tecnicos
    ):
        if tecnico[0] == ultimo_id:
            proximo_indice = (
                indice + 1
            ) % len(tecnicos)
            return tecnicos[
                proximo_indice
            ][1]
    return tecnicos[0][1]

def criar_usuario(
    nome,
    email,
    senha_hash,
    cargo,
):
    nome = nome.strip()
    email = email.strip().lower()
    cargo = cargo.strip().lower()
    if not nome:
        raise ValueError(
            "Nome é obrigatório."
        )
    if not email:
        raise ValueError(
            "E-mail é obrigatório."
        )
    if cargo not in (
        "tecnico",
        "supervisao",
    ):
        raise ValueError(
            "Cargo inválido."
        )
    with conectar() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO usuarios (
                    nome,
                    email,
                    senha_hash,
                    cargo
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s
                )
                RETURNING
                    id,
                    nome,
                    email,
                    cargo,
                    ativo,
                    trabalhando;
                """,
                (
                    nome,
                    email,
                    senha_hash,
                    cargo,
                ),
            )
            usuario = cursor.fetchone()
        conn.commit()
    return usuario

def buscar_usuario_por_email(email):
    email = email.strip().lower()
    with conectar() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    nome,
                    email,
                    senha_hash,
                    cargo,
                    ativo,
                    trabalhando
                FROM usuarios
                WHERE email = %s;
                """,
                (
                    email,
                ),
            )
            return cursor.fetchone()

def atualizar_status_trabalhando(
    usuario_id,
    trabalhando,
):
    with conectar() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE usuarios
                SET
                    trabalhando = %s,
                    ultimo_heartbeat = CASE
                        WHEN %s = TRUE THEN CURRENT_TIMESTAMP
                        ELSE NULL
                    END
                WHERE id = %s;
                """,
                (
                    trabalhando,
                    trabalhando,
                    usuario_id,
                ),
            )
        conn.commit()

def atualizar_heartbeat(usuario_id):
    with conectar() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE usuarios
                SET
                    trabalhando = TRUE,
                    ultimo_heartbeat = CURRENT_TIMESTAMP
                WHERE id = %s
                  AND cargo = 'tecnico'
                  AND ativo = TRUE;
                """,
                (
                    usuario_id,
                ),
            )
        conn.commit()

def atualizar_atribuicao_owner(
    numero_ticket,
    owner,
):
    if owner:
        owner = owner.strip()
    with conectar() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    a.id,
                    a.tecnico,
                    a.status,
                    a.tipo_atribuicao,
                    a.ultimo_tecnico_id_anterior
                FROM atribuicoes a
                WHERE a.numero_ticket = %s
                FOR UPDATE;
                """,
                (
                    numero_ticket,
                ),
            )
            atribuicao = cursor.fetchone()
            if atribuicao is None:
                conn.commit()
                return None
            (
                atribuicao_id,
                tecnico_atribuido,
                status_atual,
                tipo_atribuicao,
                ultimo_tecnico_id_anterior,
            ) = atribuicao
            cursor.execute(
                """
                SELECT
                    id,
                    nome,
                    cargo,
                    trabalhando
                FROM usuarios
                WHERE LOWER(nome) = LOWER(%s)
                  AND ativo = TRUE
                LIMIT 1;
                """,
                (
                    owner,
                ),
            )
            usuario_owner = cursor.fetchone()
            # Owner não cadastrado.
            #
            # Apenas registra o Owner.
            # A fila não é alterada.
            if usuario_owner is None:
                cursor.execute(
                    """
                    UPDATE atribuicoes
                    SET
                        owner_otrs = %s
                    WHERE id = %s;
                    """,
                    (
                        owner,
                        atribuicao_id,
                    ),
                )
                conn.commit()
                return {
                    "numero_ticket": numero_ticket,
                    "tecnico": tecnico_atribuido,
                    "owner": owner,
                    "status": status_atual,
                    "tipo_atribuicao": tipo_atribuicao,
                }
            (
                owner_id,
                owner_nome,
                owner_cargo,
                owner_trabalhando,
            ) = usuario_owner
            # Supervisão é CORINGA.
            #
            # Se o chamado ainda estava PENDENTE,
            # a atribuição inicial movimentou a fila.
            #
            # Supervisão não consome essa vez.
            # Portanto, restauramos o estado anterior.
            if owner_cargo == "supervisao":
                if (
                    status_atual == "PENDENTE"
                    and tipo_atribuicao == "TECNICO"
                ):
                    cursor.execute(
                        """
                        UPDATE fila_estado
                        SET
                            ultimo_tecnico_id = %s
                        WHERE id = 1;
                        """,
                        (
                            ultimo_tecnico_id_anterior,
                        ),
                    )
                cursor.execute(
                    """
                    UPDATE atribuicoes
                    SET
                        owner_otrs = %s,
                        status = 'CONFIRMADO',
                        tipo_atribuicao = 'SUPERVISAO',
                        confirmado_em =
                            CURRENT_TIMESTAMP
                    WHERE id = %s;
                    """,
                    (
                        owner_nome,
                        atribuicao_id,
                    ),
                )
                resultado = {
                    "numero_ticket": numero_ticket,
                    "tecnico": tecnico_atribuido,
                    "owner": owner_nome,
                    "status": "CONFIRMADO",
                    "tipo_atribuicao": "SUPERVISAO",
                }
                conn.commit()
                return resultado
            # O técnico originalmente atribuído confirmou.
            #
            # Nesse caso sabemos que ele realmente assumiu
            # o chamado. A vez já havia sido consumida
            # na atribuição inicial.
            if (
                owner_cargo == "tecnico"
                and tecnico_atribuido
                and tecnico_atribuido.lower()
                == owner_nome.lower()
            ):
                cursor.execute(
                    """
                    UPDATE atribuicoes
                    SET
                        owner_otrs = %s,
                        status = 'CONFIRMADO',
                        tipo_atribuicao = 'TECNICO',
                        confirmado_em =
                            CURRENT_TIMESTAMP
                    WHERE id = %s;
                    """,
                    (
                        owner_nome,
                        atribuicao_id,
                    ),
                )
                resultado = {
                    "numero_ticket": numero_ticket,
                    "tecnico": owner_nome,
                    "owner": owner_nome,
                    "status": "CONFIRMADO",
                    "tipo_atribuicao": "TECNICO",
                }
                conn.commit()
                return resultado
            # Outro técnico assumiu o chamado.
            #
            # Somente um técnico que esteja realmente
            # trabalhando pode consumir a vez.
            #
            # Se ele estiver fora da vez, a fila permanece.
            if owner_cargo == "tecnico":
                cursor.execute(
                    """
                    SELECT
                        ultimo_tecnico_id
                    FROM fila_estado
                    WHERE id = 1
                    FOR UPDATE;
                    """
                )
                fila = cursor.fetchone()
                ultimo_id_atual = (
                    fila[0]
                    if fila
                    else None
                )
                cursor.execute(
                    """
                    SELECT
                        id,
                        nome
                    FROM usuarios
                    WHERE cargo = 'tecnico'
                      AND ativo = TRUE
                      AND trabalhando = TRUE
                    ORDER BY id;
                    """
                )
                tecnicos = cursor.fetchall()
                proximo_tecnico_id = None
                if tecnicos:
                    if ultimo_id_atual is None:
                        proximo_tecnico_id = (
                            tecnicos[0][0]
                        )
                    else:
                        for indice, tecnico in enumerate(
                            tecnicos
                        ):
                            if (
                                tecnico[0]
                                == ultimo_id_atual
                            ):
                                proximo_indice = (
                                    indice + 1
                                ) % len(tecnicos)
                                proximo_tecnico_id = (
                                    tecnicos[
                                        proximo_indice
                                    ][0]
                                )
                                break
                        if proximo_tecnico_id is None:
                            proximo_tecnico_id = (
                                tecnicos[0][0]
                            )
                # Se o técnico que assumiu está trabalhando
                # e é exatamente o próximo da fila,
                # ele consome a vez.
                if (
                    owner_trabalhando
                    and
                    status_atual == "PENDENTE"
                    and
                    owner_id
                    == proximo_tecnico_id
                ):
                    cursor.execute(
                        """
                        UPDATE fila_estado
                        SET
                            ultimo_tecnico_id = %s
                        WHERE id = 1;
                        """,
                        (
                            owner_id,
                        ),
                    )
                cursor.execute(
                    """
                    UPDATE atribuicoes
                    SET
                        tecnico = %s,
                        owner_otrs = %s,
                        status = 'CONFIRMADO',
                        tipo_atribuicao = 'TECNICO',
                        confirmado_em =
                            CURRENT_TIMESTAMP
                    WHERE id = %s;
                    """,
                    (
                        owner_nome,
                        owner_nome,
                        atribuicao_id,
                    ),
                )
                resultado = {
                    "numero_ticket": numero_ticket,
                    "tecnico": owner_nome,
                    "owner": owner_nome,
                    "status": "CONFIRMADO",
                    "tipo_atribuicao": "TECNICO",
                }
                conn.commit()
                return resultado
            # Segurança para cargo inesperado.
            cursor.execute(
                """
                UPDATE atribuicoes
                SET
                    owner_otrs = %s
                WHERE id = %s;
                """,
                (
                    owner_nome,
                    atribuicao_id,
                ),
            )
        conn.commit()
    return {
        "numero_ticket": numero_ticket,
        "tecnico": tecnico_atribuido,
        "owner": owner_nome,
        "status": status_atual,
        "tipo_atribuicao": tipo_atribuicao,
    }
