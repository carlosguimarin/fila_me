import json
from urllib.request import urlopen


URL_ESTADO = "http://127.0.0.1:8765/estado"


def buscar_estado():
    try:
        with urlopen(URL_ESTADO, timeout=2) as resposta:
            dados = resposta.read().decode("utf-8")
            return json.loads(dados)

    except Exception:
        return None