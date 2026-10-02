import threading
import tkinter as tk

from src.fila_me.integracao.servidor_local import iniciar_servidor
from src.fila_me.ui.janela_principal import JanelaPrincipal


def iniciar_servidor_em_background():
    servidor_thread = threading.Thread(
        target=iniciar_servidor,
        daemon=True,
    )

    servidor_thread.start()


def main():
    iniciar_servidor_em_background()

    root = tk.Tk()

    JanelaPrincipal(
        root=root,
    )

    root.mainloop()


if __name__ == "__main__":
    main()