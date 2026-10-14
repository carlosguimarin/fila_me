"""Preferências locais por usuário, sem credenciais."""
import json
import os
from pathlib import Path

PALETA = {
    "Vermelho": "#FF626B", "Cereja": "#F26F9A", "Coral": "#FF8A76",
    "Laranja": "#F0A45D", "Âmbar": "#E3AF52", "Azul": "#5B9EFF",
    "Azul celeste": "#71B7F6", "Índigo": "#8F9CFF", "Roxo": "#BA93FF",
    "Violeta": "#D499F2", "Rosa": "#EE80B8", "Magenta": "#EA74DB",
}
PADRAO = {"tema": "escuro", "modo": "avancado", "cor": "#FF626B", "filtro": "todos"}
CHAVE_APARENCIA_LOGIN = "_aparencia_login"
CHAVE_ULTIMO_USUARIO = "_ultimo_usuario_id"


def caminho_preferencias():
    base = Path(os.getenv("LOCALAPPDATA") or os.getenv("XDG_CONFIG_HOME") or Path.home() / ".config")
    return base / "FilaME" / "preferencias.json"


def normalizar(valores):
    resultado = dict(PADRAO)
    if not isinstance(valores, dict):
        return resultado
    if valores.get("tema") in ("escuro", "claro"):
        resultado["tema"] = valores["tema"]
    if valores.get("modo") in ("simples", "avancado"):
        resultado["modo"] = valores["modo"]
    if valores.get("cor") in PALETA.values():
        resultado["cor"] = valores["cor"]
    if valores.get("filtro") in ("todos", "meus"):
        resultado["filtro"] = valores["filtro"]
    return resultado


def carregar(usuario_id):
    try:
        dados = json.loads(caminho_preferencias().read_text(encoding="utf-8"))
        return normalizar(dados.get(str(usuario_id), {}))
    except (OSError, ValueError, AttributeError):
        return dict(PADRAO)


def carregar_aparencia_login():
    """Carrega tema e cor da tela de login, independentemente do usuário."""
    try:
        dados = json.loads(caminho_preferencias().read_text(encoding="utf-8"))
        if not isinstance(dados, dict):
            return {"tema": PADRAO["tema"], "cor": PADRAO["cor"]}

        aparencia = dados.get(CHAVE_APARENCIA_LOGIN)
        if not isinstance(aparencia, dict):
            ultimo_usuario = dados.get(CHAVE_ULTIMO_USUARIO)
            aparencia = dados.get(str(ultimo_usuario)) if ultimo_usuario is not None else None

        # Migra instalações antigas que só possuem as preferências de uma conta.
        if not isinstance(aparencia, dict):
            contas = [
                valor for chave, valor in dados.items()
                if not chave.startswith("_") and isinstance(valor, dict)
            ]
            if len(contas) == 1:
                aparencia = contas[0]

        normalizado = normalizar(aparencia)
        return {"tema": normalizado["tema"], "cor": normalizado["cor"]}
    except (OSError, ValueError, AttributeError):
        return {"tema": PADRAO["tema"], "cor": PADRAO["cor"]}


def salvar(usuario_id, valores):
    caminho = caminho_preferencias()
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        if not isinstance(dados, dict):
            dados = {}
    except (OSError, ValueError):
        dados = {}
    normalizado = normalizar(valores)
    dados[str(usuario_id)] = normalizado
    dados[CHAVE_APARENCIA_LOGIN] = {
        "tema": normalizado["tema"],
        "cor": normalizado["cor"],
    }
    dados[CHAVE_ULTIMO_USUARIO] = str(usuario_id)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = caminho.with_suffix(".tmp")
    temporario.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    temporario.replace(caminho)
