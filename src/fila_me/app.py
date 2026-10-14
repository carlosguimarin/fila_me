import threading
import tkinter as tk
from pathlib import Path

from src.fila_me.integracao.servidor_local import (
    iniciar_servidor,
)
from src.fila_me.ui.janela_principal import (
    JanelaPrincipal,
)
from src.fila_me.ui.componentes import ExecutorUI
from src.fila_me.ui.tela_cadastro import (
    TelaCadastro,
)
from src.fila_me.ui.tela_login import (
    TelaLogin,
)


class Aplicacao:

    def __init__(self):

        self.root = tk.Tk()

        caminho_icone = Path(__file__).resolve().parent / "ui" / "assets" / "brand" / "owl-app.png"
        self.icone_aplicacao = tk.PhotoImage(file=str(caminho_icone))
        self.root.iconphoto(True, self.icone_aplicacao)
        caminho_icone_windows = caminho_icone.with_name("owl.ico")
        if caminho_icone_windows.exists():
            self.root.iconbitmap(str(caminho_icone_windows))

        self.root.title(
            "Fila ME"
        )

        self.root.geometry(
            "365x410"
        )

        self.root.minsize(
            365,
            410,
        )

        self.usuario = None
        self.janela_principal = None
        self.tela = None
        self.executor = ExecutorUI(self.root)

        self.iniciar_servidor()

        self.mostrar_login()

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.fechar,
        )

    def iniciar_servidor(self):

        thread = threading.Thread(
            target=iniciar_servidor,
            daemon=True,
        )

        thread.start()

    def limpar_tela(self):
        if self.tela is not None:
            self.tela.encerrar()
            self.tela = None
        for widget in self.root.winfo_children():
            widget.destroy()

    def mostrar_login(self):

        self.limpar_tela()

        self.tela = TelaLogin(
            self.root,
            ao_logar=self.entrar,
            ao_cadastrar=self.mostrar_cadastro,
            executor=self.executor,
        )

    def mostrar_cadastro(self):

        self.limpar_tela()

        self.tela = TelaCadastro(
            self.root,
            ao_voltar=self.mostrar_login,
            executor=self.executor,
        )

    def entrar(self, usuario):

        self.usuario = usuario

        self.limpar_tela()

        self.janela_principal = (
            JanelaPrincipal(
                self.root,
                usuario,
                ao_sair=self.sair,
                executor=self.executor,
            )
        )
        self.tela = self.janela_principal

    def sair(self):

        if self.janela_principal:
            self.janela_principal.encerrar()

        self.janela_principal = None
        self.usuario = None

        self.mostrar_login()

    def fechar(self):
        self.limpar_tela()
        self.executor.encerrar()
        self.root.destroy()


def main():

    aplicacao = Aplicacao()

    aplicacao.root.mainloop()


if __name__ == "__main__":
    main()
