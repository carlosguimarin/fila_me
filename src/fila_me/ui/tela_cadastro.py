import tkinter as tk
from tkinter import messagebox, ttk

from src.fila_me.database.autenticacao import (
    cadastrar_usuario,
)


class TelaCadastro:

    def __init__(
        self,
        root,
        ao_voltar,
    ):
        self.root = root
        self.ao_voltar = ao_voltar

        self.frame = tk.Frame(
            root,
            bg="#202124",
        )

        self.frame.pack(
            fill="both",
            expand=True,
        )

        self.criar_interface()

    def criar_interface(self):

        tk.Label(
            self.frame,
            text="Criar usuário",
            bg="#202124",
            fg="#F1F3F4",
            font=("Segoe UI", 18, "bold"),
        ).pack(
            pady=(30, 20)
        )

        tk.Label(
            self.frame,
            text="Nome",
            bg="#202124",
            fg="#F1F3F4",
            font=("Segoe UI", 10),
        ).pack(
            anchor="w",
            padx=40,
        )

        self.campo_nome = tk.Entry(
            self.frame,
            font=("Segoe UI", 11),
        )

        self.campo_nome.pack(
            fill="x",
            padx=40,
            pady=(5, 15),
        )

        tk.Label(
            self.frame,
            text="E-mail",
            bg="#202124",
            fg="#F1F3F4",
            font=("Segoe UI", 10),
        ).pack(
            anchor="w",
            padx=40,
        )

        self.campo_email = tk.Entry(
            self.frame,
            font=("Segoe UI", 11),
        )

        self.campo_email.pack(
            fill="x",
            padx=40,
            pady=(5, 15),
        )

        tk.Label(
            self.frame,
            text="Senha",
            bg="#202124",
            fg="#F1F3F4",
            font=("Segoe UI", 10),
        ).pack(
            anchor="w",
            padx=40,
        )

        self.campo_senha = tk.Entry(
            self.frame,
            show="*",
            font=("Segoe UI", 11),
        )

        self.campo_senha.pack(
            fill="x",
            padx=40,
            pady=(5, 15),
        )

        tk.Label(
            self.frame,
            text="Cargo",
            bg="#202124",
            fg="#F1F3F4",
            font=("Segoe UI", 10),
        ).pack(
            anchor="w",
            padx=40,
        )

        self.campo_cargo = ttk.Combobox(
            self.frame,
            values=[
                "Técnico",
                "Supervisão",
            ],
            state="readonly",
            font=("Segoe UI", 11),
        )

        self.campo_cargo.pack(
            fill="x",
            padx=40,
            pady=(5, 20),
        )

        botoes = tk.Frame(
            self.frame,
            bg="#202124",
        )

        botoes.pack()

        tk.Button(
            botoes,
            text="Voltar",
            command=self.voltar,
            bg="#34363A",
            fg="#F1F3F4",
            activebackground="#45474B",
            activeforeground="#FFFFFF",
            relief="flat",
            padx=20,
            pady=8,
        ).pack(
            side="left",
            padx=5,
        )

        tk.Button(
            botoes,
            text="Cadastrar",
            command=self.cadastrar,
            bg="#4F8CFF",
            fg="#FFFFFF",
            activebackground="#6A9CFF",
            activeforeground="#FFFFFF",
            relief="flat",
            padx=20,
            pady=8,
        ).pack(
            side="left",
            padx=5,
        )

    def cadastrar(self):

        nome = self.campo_nome.get().strip()
        email = self.campo_email.get().strip()
        senha = self.campo_senha.get()
        cargo = self.campo_cargo.get()

        if not nome:
            messagebox.showwarning(
                "Cadastro",
                "Informe o nome.",
            )
            return

        if not email:
            messagebox.showwarning(
                "Cadastro",
                "Informe o e-mail.",
            )
            return

        if not senha:
            messagebox.showwarning(
                "Cadastro",
                "Informe a senha.",
            )
            return

        if cargo == "":
            messagebox.showwarning(
                "Cadastro",
                "Selecione o cargo.",
            )
            return

        cargo_banco = {
            "Técnico": "tecnico",
            "Supervisão": "supervisao",
        }[cargo]

        try:

            cadastrar_usuario(
                nome=nome,
                email=email,
                senha=senha,
                cargo=cargo_banco,
            )

        except Exception as erro:

            if "duplicate key" in str(erro).lower():
                messagebox.showerror(
                    "Cadastro",
                    "Este e-mail já está cadastrado.",
                )
            else:
                messagebox.showerror(
                    "Cadastro",
                    f"Erro ao cadastrar usuário:\n\n{erro}",
                )

            return

        messagebox.showinfo(
            "Cadastro",
            "Usuário cadastrado com sucesso.",
        )

        self.voltar()

    def voltar(self):

        self.frame.destroy()
        self.ao_voltar()