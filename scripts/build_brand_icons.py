"""Gera os formatos do mascote FILA ME a partir da arte aprovada."""
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "src/fila_me/ui/assets/brand/owl.png"
BRAND_DIR = MASTER.parent
EXTENSION_DIR = ROOT / "browser_extension/icons"
CANVAS_SIZE = 1024


def criar_matriz():
    original = Image.open(MASTER).convert("RGBA")
    # Mantém a arte inteira, com transparência, em uma tela quadrada com margem.
    original.thumbnail((round(CANVAS_SIZE * 0.92),) * 2, Image.Resampling.LANCZOS)
    tela = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), (0, 0, 0, 0))
    tela.alpha_composite(
        original,
        ((CANVAS_SIZE - original.width) // 2, (CANVAS_SIZE - original.height) // 2),
    )
    return tela


def main():
    matriz = criar_matriz()
    matriz.save(BRAND_DIR / "owl-app.png", optimize=True)
    matriz.save(
        BRAND_DIR / "owl.ico",
        format="ICO",
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    for tamanho in (16, 32, 48, 128):
        matriz.resize((tamanho, tamanho), Image.Resampling.LANCZOS).save(
            EXTENSION_DIR / f"owl-{tamanho}.png",
            optimize=True,
        )


if __name__ == "__main__":
    main()
