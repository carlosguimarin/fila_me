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


def salvar(usuario_id, valores):
    caminho = caminho_preferencias()
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        if not isinstance(dados, dict):
            dados = {}
    except (OSError, ValueError):
        dados = {}
    dados[str(usuario_id)] = normalizar(valores)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = caminho.with_suffix(".tmp")
    temporario.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    temporario.replace(caminho)
