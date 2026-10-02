import os

import psycopg
from dotenv import load_dotenv


import sys


if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(
        sys.executable
    )
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

TECNICOS = ["Carlos", "Luis", "Daniel"]


def conectar():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL não encontrada no arquivo .env")

    return psycopg.connect(DATABASE_URL)


def criar_tabelas():
    with conectar() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    numero_ticket BIGINT PRIMARY KEY,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fila_estado (
                    id INTEGER PRIMARY KEY,
                    indice_atual INTEGER NOT NULL
                );
            """)

            cursor.execute("""
                INSERT INTO fila_estado (id, indice_atual)
                VALUES (1, 0)
                ON CONFLICT (id) DO NOTHING;
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS atribuicoes (
                    id BIGSERIAL PRIMARY KEY,
                    numero_ticket BIGINT NOT NULL UNIQUE
                        REFERENCES tickets(numero_ticket),
                    tecnico VARCHAR(50) NOT NULL,
                    atribuido_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

        conn.commit()


def criar_tabela_tickets():
    criar_tabelas()


def registrar_ticket(numero_ticket):
    with conectar() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tickets (numero_ticket)
                VALUES (%s)
                ON CONFLICT (numero_ticket) DO NOTHING
                RETURNING numero_ticket;
                """,
                (numero_ticket,),
            )

            resultado = cursor.fetchone()

        conn.commit()

    return resultado is not None


def registrar_ticket_e_atribuir(numero_ticket):
    with conectar() as conn:
        with conn.cursor() as cursor:

            # Tenta registrar o ticket.
            cursor.execute(
                """
                INSERT INTO tickets (numero_ticket)
                VALUES (%s)
                ON CONFLICT (numero_ticket) DO NOTHING
                RETURNING numero_ticket;
                """,
                (numero_ticket,),
            )

            ticket_novo = cursor.fetchone()

            # Ticket já existia.
            if ticket_novo is None:
                conn.commit()
                return None

            # Bloqueia o estado da fila para evitar
            # dois computadores pegarem o mesmo técnico.
            cursor.execute(
                """
                SELECT indice_atual
                FROM fila_estado
                WHERE id = 1
                FOR UPDATE;
                """
            )

            indice_atual = cursor.fetchone()[0]
            tecnico = TECNICOS[indice_atual]

            # Registra a atribuição.
            cursor.execute(
                """
                INSERT INTO atribuicoes (
                    numero_ticket,
                    tecnico
                )
                VALUES (%s, %s);
                """,
                (numero_ticket, tecnico),
            )

            # Avança a fila.
            proximo_indice = (
                indice_atual + 1
            ) % len(TECNICOS)

            cursor.execute(
                """
                UPDATE fila_estado
                SET indice_atual = %s
                WHERE id = 1;
                """,
                (proximo_indice,),
            )

        conn.commit()

    return {
        "numero_ticket": numero_ticket,
        "tecnico": tecnico,
    }


def buscar_ultimas_atribuicoes(limite=9):
    with conectar() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    numero_ticket,
                    tecnico,
                    atribuido_em
                FROM atribuicoes
                ORDER BY id DESC
                LIMIT %s;
                """,
                (limite,),
            )

            return cursor.fetchall()


def buscar_proximo_tecnico():
    with conectar() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT indice_atual
                FROM fila_estado
                WHERE id = 1;
                """
            )

            indice_atual = cursor.fetchone()[0]

    return TECNICOS[indice_atual]