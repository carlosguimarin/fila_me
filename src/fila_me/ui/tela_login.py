import tkinter as tk
from tkinter import messagebox

from src.fila_me.database.autenticacao import (
    autenticar_usuario,
)

from src.fila_me.ui.estilos import (
    COR_FUNDO,
    COR_TEXTO,
    COR_SECUNDARIO,
    COR_DESTAQUE,
    FONTE_PADRAO,
)


class TelaLogin:

    def __init__(
        self,
        root,
        ao_logar,
        ao_cadastrar,
    ):

        self.root = root
        self.ao_logar = ao_logar
        self.ao_cadastrar = ao_cadastrar

        self.criar_interface()

    def limpar(self):

        for widget in self.root.winfo_children():
            widget.destroy()

    def criar_interface(self):

        self.limpar()

        self.root.title(
            "Fila N1 - Login"
        )

        self.root.geometry(
            "360x360"
        )

        self.root.resizable(
            False,
            False,
        )

        self.root.configure(
            bg=COR_FUNDO
        )

        titulo = tk.Label(
            self.root,
            text="FILA N1",
            bg=COR_FUNDO,
            fg=COR_TEXTO,
            font=(
                FONTE_PADRAO,
                24,
                "bold",
            ),
        )

        titulo.pack(
            pady=(35, 5)
        )

        subtitulo = tk.Label(
            self.root,
            text="Entrar",
            bg=COR_FUNDO,
            fg=COR_SECUNDARIO,
            font=(
                FONTE_PADRAO,
                10,
            ),
        )

        subtitulo.pack(
            pady=(0, 25)
        )

        tk.Label(
            self.root,
            text="E-mail",
            bg=COR_FUNDO,
            fg=COR_SECUNDARIO,
            font=(FONTE_PADRAO, 9),
        ).pack(
            anchor="w",
            padx=45,
        )

        self.email_entry = tk.Entry(
            self.root,
            font=(
                FONTE_PADRAO,
                11,
            ),
            relief="flat",
        )

        self.email_entry.pack(
            fill="x",
            padx=45,
            ipady=6,
        )

        self.email_entry.bind(
            "<Return>",
            self.ir_para_senha,
        )

        tk.Label(
            self.root,
            text="Senha",
            bg=COR_FUNDO,
            fg=COR_SECUNDARIO,
            font=(FONTE_PADRAO, 9),
        ).pack(
            anchor="w",
            padx=45,
            pady=(15, 0),
        )

        self.senha_entry = tk.Entry(
            self.root,
            show="*",
            font=(
                FONTE_PADRAO,
                11,
            ),
            relief="flat",
        )

        self.senha_entry.pack(
            fill="x",
            padx=45,
            ipady=6,
        )

        self.senha_entry.bind(
            "<Return>",
            self.entrar_com_enter,
        )

        botao = tk.Button(
            self.root,
            text="Entrar",
            command=self.entrar,
            bg=COR_DESTAQUE,
            fg="white",
            relief="flat",
            bd=0,
            font=(
                FONTE_PADRAO,
                10,
                "bold",
            ),
            cursor="hand2",
        )

        botao.pack(
            fill="x",
            padx=45,
            pady=(25, 10),
            ipady=6,
        )

        cadastro = tk.Button(
            self.root,
            text="Criar cadastro",
            command=self.ao_cadastrar,
            bg=COR_FUNDO,
            fg=COR_SECUNDARIO,
            activebackground=COR_FUNDO,
            activeforeground=COR_TEXTO,
            relief="flat",
            bd=0,
            font=(
                FONTE_PADRAO,
                9,
            ),
            cursor="hand2",
        )

        cadastro.pack()

        self.email_entry.focus_set()

    def ir_para_senha(self, evento=None):

        self.senha_entry.focus_set()

        return "break"

    def entrar_com_enter(self, evento=None):

        self.entrar()

        return "break"

    def entrar(self):

        email = self.email_entry.get().strip()
        senha = self.senha_entry.get()

        if not email or not senha:

            messagebox.showwarning(
                "Login",
                "Informe o e-mail e a senha.",
            )

            return

        try:

            usuario = autenticar_usuario(
                email,
                senha,
            )

        except Exception as erro:

            messagebox.showerror(
                "Erro",
                f"Não foi possível realizar o login:\n\n{erro}",
            )

            return

        if usuario is None:

            messagebox.showerror(
                "Login",
                "E-mail ou senha inválidos.",
            )

            return

        self.ao_logar(usuario)