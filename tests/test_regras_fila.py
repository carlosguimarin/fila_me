def escolher_proximo_tecnico(tecnicos, ultimo_tecnico_id):
    if not tecnicos:
        return None

    if ultimo_tecnico_id is None:
        return tecnicos[0]

    for indice, tecnico in enumerate(tecnicos):

        if tecnico["id"] == ultimo_tecnico_id:

            proximo_indice = (
                indice + 1
            ) % len(tecnicos)

            return tecnicos[proximo_indice]

    return tecnicos[0]


def test_primeiro_tecnico():
    tecnicos = [
        {"id": 1, "nome": "Carlos"},
        {"id": 2, "nome": "Luis"},
        {"id": 3, "nome": "Daniel"},
    ]

    resultado = escolher_proximo_tecnico(
        tecnicos,
        None,
    )

    assert resultado["nome"] == "Carlos"


def test_carlos_depois_luis():
    tecnicos = [
        {"id": 1, "nome": "Carlos"},
        {"id": 2, "nome": "Luis"},
        {"id": 3, "nome": "Daniel"},
    ]

    resultado = escolher_proximo_tecnico(
        tecnicos,
        1,
    )

    assert resultado["nome"] == "Luis"


def test_luis_depois_daniel():
    tecnicos = [
        {"id": 1, "nome": "Carlos"},
        {"id": 2, "nome": "Luis"},
        {"id": 3, "nome": "Daniel"},
    ]

    resultado = escolher_proximo_tecnico(
        tecnicos,
        2,
    )

    assert resultado["nome"] == "Daniel"


def test_daniel_volta_para_carlos():
    tecnicos = [
        {"id": 1, "nome": "Carlos"},
        {"id": 2, "nome": "Luis"},
        {"id": 3, "nome": "Daniel"},
    ]

    resultado = escolher_proximo_tecnico(
        tecnicos,
        3,
    )

    assert resultado["nome"] == "Carlos"


def test_tecnico_fora_da_lista_volta_para_primeiro():
    tecnicos = [
        {"id": 1, "nome": "Carlos"},
        {"id": 2, "nome": "Luis"},
        {"id": 3, "nome": "Daniel"},
    ]

    resultado = escolher_proximo_tecnico(
        tecnicos,
        999,
    )

    assert resultado["nome"] == "Carlos"


def test_sem_tecnicos():
    resultado = escolher_proximo_tecnico(
        [],
        None,
    )

    assert resultado is None


def test_supervisao_nao_consumiu_a_vez():
    tecnicos = [
        {"id": 1, "nome": "Carlos"},
        {"id": 2, "nome": "Luis"},
        {"id": 3, "nome": "Daniel"},
    ]

    # Antes da atribuição:
    # Daniel foi o último.
    # Portanto Carlos é o próximo.
    ultimo_antes = 3

    # A atribuição provisória para Carlos
    # movimentaria temporariamente a fila.
    ultimo_depois_atribuicao = 1

    # Supervisão assume.
    # A fila deve voltar ao estado anterior.
    ultimo_depois_supervisao = ultimo_antes

    resultado = escolher_proximo_tecnico(
        tecnicos,
        ultimo_depois_supervisao,
    )

    assert ultimo_depois_atribuicao == 1
    assert resultado["nome"] == "Carlos"


def test_outro_tecnico_nao_altera_a_fila():
    tecnicos = [
        {"id": 1, "nome": "Carlos"},
        {"id": 2, "nome": "Luis"},
        {"id": 3, "nome": "Daniel"},
    ]

    # Carlos recebeu a atribuição.
    # Carlos continua sendo o último da fila.
    ultimo_antes_owner = 1

    # Luís assumiu o chamado fora da vez.
    # A fila NÃO deve ser alterada.
    ultimo_depois_owner = ultimo_antes_owner

    resultado = escolher_proximo_tecnico(
        tecnicos,
        ultimo_depois_owner,
    )

    assert resultado["nome"] == "Luis"