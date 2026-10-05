import hashlib
import hmac
import secrets

from src.fila_me.database.banco import (
    criar_usuario,
    buscar_usuario_por_email,
)


ALGORITMO = "sha256"
ITERACOES = 600_000
TAMANHO_SALT = 16


def gerar_hash_senha(senha):

    if not senha:
        raise ValueError(
            "Senha é obrigatória."
        )

    salt = secrets.token_bytes(
        TAMANHO_SALT
    )

    hash_senha = hashlib.pbkdf2_hmac(
        ALGORITMO,
        senha.encode("utf-8"),
        salt,
        ITERACOES,
    )

    return (
        f"pbkdf2_{ALGORITMO}"
        f"${ITERACOES}"
        f"${salt.hex()}"
        f"${hash_senha.hex()}"
    )


def verificar_senha(
    senha,
    senha_hash,
):

    try:

        algoritmo, iteracoes, salt_hex, hash_hex = (
            senha_hash.split("$")
        )

        if algoritmo != "pbkdf2_sha256":
            return False

        salt = bytes.fromhex(
            salt_hex
        )

        hash_esperado = bytes.fromhex(
            hash_hex
        )

        hash_atual = hashlib.pbkdf2_hmac(
            ALGORITMO,
            senha.encode("utf-8"),
            salt,
            int(iteracoes),
        )

        return hmac.compare_digest(
            hash_atual,
            hash_esperado,
        )

    except (
        ValueError,
        TypeError,
    ):
        return False


def cadastrar_usuario(
    nome,
    email,
    senha,
    cargo,
):

    senha_hash = gerar_hash_senha(
        senha
    )

    return criar_usuario(
        nome=nome,
        email=email,
        senha_hash=senha_hash,
        cargo=cargo,
    )


def autenticar_usuario(
    email,
    senha,
):

    usuario = buscar_usuario_por_email(
        email
    )

    if usuario is None:
        return None

    (
        usuario_id,
        nome,
        email_usuario,
        senha_hash,
        cargo,
        ativo,
        trabalhando,
    ) = usuario

    if not ativo:
        return None

    if not verificar_senha(
        senha,
        senha_hash,
    ):
        return None

    return {
        "id": usuario_id,
        "nome": nome,
        "email": email_usuario,
        "cargo": cargo,
        "ativo": ativo,
        "trabalhando": trabalhando,
    }