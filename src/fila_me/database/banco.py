import os

import psycopg
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def conectar():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL não encontrada no arquivo .env")

    return psycopg.connect(DATABASE_URL)


def criar_tabela_tickets():
    with conectar() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    numero_ticket BIGINT PRIMARY KEY,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

        conn.commit()


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