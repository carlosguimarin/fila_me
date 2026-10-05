import tkinter as tk

from src.fila_me.database.banco import (
    atualizar_status_trabalhando,
    buscar_ultimas_atribuicoes,
    buscar_proximo_tecnico,
)


class JanelaPrincipal:

    def __init__(
        self,
        root,
        usuario,
        ao_sair,
    ):
        self.root = root
        self.usuario = usuario
        self.ao_sair = ao_sair

        self.frame = tk.Frame(
            root,
            bg="#202124",
        )

        self.frame.pack(
            fill="both",
            expand=True,
        )

        if self.usuario["cargo"] == "tecnico":
            atualizar_status_trabalhando(
                self.usuario["id"],
                True,
            )

        self.criar_interface()
        self.atualizar_estado()

    def criar_interface(self):

        cabecalho = tk.Frame(
            self.frame,
            bg="#202124",
        )

        cabecalho.pack(
            fill="x",
            padx=20,
            pady=15,
        )

        informacoes = tk.Frame(
            cabecalho,
            bg="#202124",
        )

        informacoes.pack(
            side="left",
        )

        tk.Label(
            informacoes,
            text=self.usuario["nome"].split()[0],
            bg="#202124",
            fg="#F1F3F4",
            font=("Segoe UI", 12, "bold"),
        ).pack(
            anchor="w",
        )

        cargo = (
            "Técnico"
            if self.usuario["cargo"] == "tecnico"
            else "Supervisão"
        )

        tk.Label(
            informacoes,
            text=cargo,
            bg="#202124",
            fg="#AEB4BD",
            font=("Segoe UI", 9),
        ).pack(
            anchor="w",
        )

        tk.Button(
            cabecalho,
            text="Sair",
            command=self.sair,
            bg="#34363A",
            fg="#F1F3F4",
            activebackground="#45474B",
            activeforeground="#FFFFFF",
            relief="flat",
            padx=15,
            pady=6,
        ).pack(
            side="right",
        )

        tk.Label(
            self.frame,
            text="Fila ME",
            bg="#202124",
            fg="#F1F3F4",
            font=("Segoe UI", 20, "bold"),
        ).pack(
            pady=(10, 5),
        )

        self.label_proximo = tk.Label(
            self.frame,
            text="Próximo: carregando...",
            bg="#202124",
            fg="#4F8CFF",
            font=("Segoe UI", 13, "bold"),
        )

        self.label_proximo.pack(
            pady=10,
        )

        tk.Label(
            self.frame,
            text="Últimas atribuições",
            bg="#202124",
            fg="#F1F3F4",
            font=("Segoe UI", 11, "bold"),
        ).pack(
            pady=(15, 5),
        )

        self.lista = tk.Frame(
            self.frame,
            bg="#292A2D",
        )

        self.lista.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20),
        )

    def atualizar_estado(self):

        try:

            proximo = buscar_proximo_tecnico()

            self.label_proximo.config(
                text=f"Próximo: {proximo.split()[0]}"
            )

            self.atualizar_historico()

        except Exception as erro:

            self.label_proximo.config(
                text=f"Erro: {erro}"
            )

        self.root.after(
            5000,
            self.atualizar_estado,
        )

    def atualizar_historico(self):

        for widget in self.lista.winfo_children():
            widget.destroy()

        atribuicoes = buscar_ultimas_atribuicoes(9)

        for (
            numero_ticket,
            tecnico,
            atribuido_em,
        ) in atribuicoes:

            tecnico = (
                tecnico
                if tecnico
                else "Aguardando técnico"
            )

            texto = (
                f"#{numero_ticket}  →  "
                f"{tecnico}"
            )

            tk.Label(
                self.lista,
                text=texto,
                bg="#292A2D",
                fg="#F1F3F4",
                font=("Segoe UI", 10),
                anchor="w",
            ).pack(
                fill="x",
                padx=15,
                pady=5,
            )

    def sair(self):

        self.encerrar()

        self.ao_sair()

    def encerrar(self):

        if self.usuario["cargo"] == "tecnico":

            atualizar_status_trabalhando(
                self.usuario["id"],
                False,
            )

        self.frame.destroy()