import tkinter as tk

from src.fila_me.models.fila import Fila
from src.fila_me.ui.janela_principal import JanelaPrincipal


def main():
    fila = Fila()

    root = tk.Tk()

    JanelaPrincipal(
        root=root,
        fila=fila,
    )

    root.mainloop()


if __name__ == "__main__":
    main()