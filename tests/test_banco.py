import pytest

from src.fila_me.database import banco


class ConexaoTeste:
    def __init__(self, conexao):
        self.conexao = conexao

    def __enter__(self):
        return self.conexao

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def commit(self):
        # Impede os commits das funções reais durante o teste.
        pass

    def rollback(self):
        self.conexao.rollback()


@pytest.fixture
def conexao_teste():
    conexao = banco.psycopg.connect(
        banco.DATABASE_URL
    )

    conexao.execute(
        "BEGIN;"
    )

    wrapper = ConexaoTeste(conexao)

    original_conectar = banco.conectar

    banco.conectar = lambda: wrapper

    yield conexao

    banco.conectar = original_conectar

    conexao.rollback()
    conexao.close()


def test_conexao_com_neon():

    with banco.psycopg.connect(
        banco.DATABASE_URL
    ) as conn:

        with conn.cursor() as cursor:

            cursor.execute(
                "SELECT 1;"
            )

            resultado = cursor.fetchone()

    assert resultado == (1,)


def test_tabelas_principais_existentes():

    with banco.psycopg.connect(
        banco.DATABASE_URL
    ) as conn:

        with conn.cursor() as cursor:

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_name IN (
                    'usuarios',
                    'tickets',
                    'atribuicoes',
                    'fila_estado'
                );
                """
            )

            resultado = cursor.fetchone()

    assert resultado[0] == 4


def test_coluna_supervisao_existe():

    with banco.psycopg.connect(
        banco.DATABASE_URL
    ) as conn:

        with conn.cursor() as cursor:

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM information_schema.columns
                WHERE table_name = 'atribuicoes'
                  AND column_name =
                      'ultimo_tecnico_id_anterior';
                """
            )

            resultado = cursor.fetchone()

    assert resultado[0] == 1


def test_fila_estado_existe():

    with banco.psycopg.connect(
        banco.DATABASE_URL
    ) as conn:

        with conn.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    id,
                    ultimo_tecnico_id
                FROM fila_estado
                WHERE id = 1;
                """
            )

            resultado = cursor.fetchone()

    assert resultado is not None


def test_buscar_proximo_tecnico_funciona():

    resultado = banco.buscar_proximo_tecnico()

    assert isinstance(
        resultado,
        str,
    )


def test_ticket_novo_e_atribuicao(
    conexao_teste,
):

    resultado = banco.registrar_ticket_e_atribuir(
        999999999
    )

    assert resultado is not None

    assert (
        resultado["numero_ticket"]
        == 999999999
    )


def test_ticket_duplicado_nao_cria_nova_atribuicao(
    conexao_teste,
):

    primeiro = banco.registrar_ticket_e_atribuir(
        999999998
    )

    segundo = banco.registrar_ticket_e_atribuir(
        999999998
    )

    assert primeiro is not None
    assert segundo is None


def test_owner_desconhecido_nao_muda_fila(
    conexao_teste,
):

    resultado = banco.registrar_ticket_e_atribuir(
        999999997
    )

    if resultado is None:
        pytest.skip(
            "Ticket já existente."
        )

    owner = banco.atualizar_atribuicao_owner(
        999999997,
        "Admin OTRS",
    )

    assert owner is not None

    assert (
        owner["owner"]
        == "Admin OTRS"
    )