"""Imagens Lucide locais, com antialiasing, cache e coloração por tema."""
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageTk

PASTA_ICONES = Path(__file__).resolve().parent / "assets" / "icones"


@lru_cache(maxsize=256)
def imagem_icone(nome, tamanho, cor):
    """Cache da imagem PIL; não depende da criação de uma janela Tk."""
    with Image.open(PASTA_ICONES / f"{nome}.png") as arquivo:
        # Aceita tanto PNGs RGBA quanto máscaras em tons de cinza.
        original = arquivo.convert("RGBA")
        mascara = (
            arquivo.convert("L")
            if arquivo.mode in ("1", "L", "I", "F")
            else original.getchannel("A")
        )
    imagem=Image.new("RGBA",original.size,cor)
    imagem.putalpha(mascara)
    return imagem.resize((tamanho,tamanho),Image.Resampling.LANCZOS)


@lru_cache(maxsize=256)
def carregar_icone(nome, tamanho, cor, master):
    return ImageTk.PhotoImage(imagem_icone(nome,round(tamanho),cor),master=master)
