import tkinter as tk

from src.fila_me.database.banco import (
    atualizar_heartbeat,
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

        self.sempre_no_topo = False
        self.heartbeat_id = None
        self.encerrando = False

        self.root.geometry("365x410")
        self.root.resizable(False, False)

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

            self.enviar_heartbeat()

        self.criar_interface()
        self.atualizar_estado()

    def criar_interface(self):

        cabecalho = tk.Frame(
            self.frame,
            bg="#202124",
            height=48,
        )

        cabecalho.pack(
            fill="x",
            padx=18,
            pady=(8, 1),
        )

        cabecalho.pack_propagate(False)

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

        titulo = tk.Label(
            cabecalho,
            text="Fila ME",
            bg="#202124",
            fg="#F1F3F4",
            font=("Segoe UI", 17, "bold"),
            bd=0,
            highlightthickness=0,
            padx=0,
            pady=0,
        )

        titulo.place(
            relx=0.5,
            y=3,
            anchor="n",
        )

        botoes = tk.Frame(
            cabecalho,
            bg="#202124",
        )

        botoes.pack(
            side="right",
        )

        self.botao_topo = tk.Button(
            botoes,
            text="📌︎",
            command=self.alternar_sempre_no_topo,
            bg="#202124",
            fg="#AEB4BD",
            activebackground="#202124",
            activeforeground="#FF4D4D",
            relief="flat",
            bd=0,
            highlightthickness=0,
            font=("Segoe UI Symbol", 11),
            padx=2,
            pady=2,
            cursor="hand2",
        )

        self.botao_topo.pack(
            side="left",
            padx=(0, 6),
        )

        tk.Button(
            botoes,
            text="Sair",
            command=self.sair,
            bg="#34363A",
            fg="#F1F3F4",
            activebackground="#45474B",
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            padx=12,
            pady=5,
            cursor="hand2",
        ).pack(
            side="left",
        )

        self.label_proximo = tk.Label(
            self.frame,
            text="Próximo: carregando...",
            bg="#202124",
            fg="#4F8CFF",
            font=("Segoe UI", 17, "bold"),
        )

        self.label_proximo.pack(
            pady=(3, 4),
        )

        tk.Label(
            self.frame,
            text="Últimas atribuições",
            bg="#202124",
            fg="#F1F3F4",
            font=("Segoe UI", 11, "bold"),
        ).pack(
            pady=(2, 4),
        )

        self.lista = tk.Frame(
            self.frame,
            bg="#292A2D",
        )

        self.lista.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=(0, 8),
        )

    def alternar_sempre_no_topo(self):

        self.sempre_no_topo = (
            not self.sempre_no_topo
        )

        self.root.attributes(
            "-topmost",
            self.sempre_no_topo,
        )

        if self.sempre_no_topo:

            self.botao_topo.config(
                fg="#FF4D4D",
            )

        else:

            self.botao_topo.config(
                fg="#AEB4BD",
            )

    def enviar_heartbeat(self):

        if self.encerrando:
            return

        if self.usuario["cargo"] != "tecnico":
            return

        try:

            atualizar_heartbeat(
                self.usuario["id"],
            )

        except Exception as erro:

            print(
                f"Erro ao enviar heartbeat: {erro}"
            )

        self.heartbeat_id = self.root.after(
            5000,
            self.enviar_heartbeat,
        )

    def atualizar_estado(self):

        if self.encerrando:
            return

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

        if not self.encerrando:

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

            if (
                self.usuario["cargo"] == "tecnico"
                and tecnico.lower() == self.usuario["nome"].lower()
            ):
                cor_texto = "#FF5C5C"

            else:
                cor_texto = "#F1F3F4"

            campo = tk.Entry(
                self.lista,
                bg="#292A2D",
                fg=cor_texto,
                readonlybackground="#292A2D",
                selectbackground="#4F8CFF",
                selectforeground="#FFFFFF",
                relief="flat",
                bd=0,
                highlightthickness=0,
                font=("Segoe UI", 10),
                cursor="arrow",
            )

            campo.insert(
                0,
                texto,
            )

            campo.config(
                state="readonly",
            )

            campo.pack(
                fill="x",
                padx=10,
                pady=3,
            )

    def sair(self):

        self.encerrar()

        self.ao_sair()

    def encerrar(self):

        if self.encerrando:
            return

        self.encerrando = True

        if self.heartbeat_id is not None:

            try:
                self.root.after_cancel(
                    self.heartbeat_id
                )

            except Exception:
                pass

            self.heartbeat_id = None

        self.root.attributes(
            "-topmost",
            False,
        )

        if self.usuario["cargo"] == "tecnico":

            atualizar_status_trabalhando(
                self.usuario["id"],
                False,
            )

        self.frame.destroy()