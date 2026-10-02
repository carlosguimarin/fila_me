import tkinter as tk

from src.fila_me.config.settings import (
    NOME_APLICACAO,
)

from src.fila_me.ui.estilos import (
    COR_FUNDO,
    COR_TEXTO,
    COR_SECUNDARIO,
    COR_DESTAQUE,
    COR_BOTAO,
    FONTE_PADRAO,
)

from src.fila_me.integracao.cliente import buscar_estado


class JanelaPrincipal:
    def __init__(self, root, fila=None):
        self.root = root
        self.fila = fila
        self.fixado = True

        self.configurar_janela()
        self.criar_interface()
        self.atualizar_estado()

    def configurar_janela(self):
        self.root.title(NOME_APLICACAO)

        self.root.geometry("380x430")

        self.root.resizable(False, False)

        self.root.configure(
            bg=COR_FUNDO
        )

        self.root.attributes(
            "-topmost",
            True,
        )

    def criar_interface(self):

        # -------------------------
        # TÍTULO
        # -------------------------

        titulo = tk.Label(
            self.root,
            text="FILA N1",
            bg=COR_FUNDO,
            fg=COR_SECUNDARIO,
            font=(FONTE_PADRAO, 11, "bold"),
        )

        titulo.pack(
            pady=(14, 2)
        )

        # -------------------------
        # PRÓXIMO TÉCNICO
        # -------------------------

        subtitulo = tk.Label(
            self.root,
            text="Próximo técnico",
            bg=COR_FUNDO,
            fg=COR_SECUNDARIO,
            font=(FONTE_PADRAO, 9),
        )

        subtitulo.pack()

        self.nome_label = tk.Label(
            self.root,
            text="—",
            bg=COR_FUNDO,
            fg=COR_TEXTO,
            font=(FONTE_PADRAO, 27, "bold"),
        )

        self.nome_label.pack(
            pady=(0, 12)
        )

        # -------------------------
        # HISTÓRICO
        # -------------------------

        historico_titulo = tk.Label(
            self.root,
            text="Últimos chamados",
            bg=COR_FUNDO,
            fg=COR_SECUNDARIO,
            font=(FONTE_PADRAO, 9, "bold"),
        )

        historico_titulo.pack(
            anchor="w",
            padx=20,
        )

        self.frame_historico = tk.Frame(
            self.root,
            bg=COR_FUNDO,
        )

        self.frame_historico.pack(
            fill="x",
            padx=20,
            pady=(5, 0),
        )

        # -------------------------
        # BOTÃO FIXAR
        # -------------------------

        self.btn_fixar = tk.Button(
            self.root,
            text="📌  Fixado no topo",
            command=self.alternar_fixacao,
            bg=COR_FUNDO,
            fg=COR_SECUNDARIO,
            activebackground=COR_FUNDO,
            activeforeground=COR_TEXTO,
            relief="flat",
            bd=0,
            font=(FONTE_PADRAO, 8),
            cursor="hand2",
        )

        self.btn_fixar.pack(
            pady=(8, 0)
        )

    def atualizar_estado(self):

        estado = buscar_estado()

        if estado and estado.get("sucesso"):

            proximo = estado.get(
                "proximo_tecnico",
                "—",
            )

            historico = estado.get(
                "historico",
                [],
            )

            self.nome_label.config(
                text=proximo
            )

            self.atualizar_historico(
                historico
            )

        self.root.after(
            3000,
            self.atualizar_estado,
        )

    def atualizar_historico(self, historico):

        for widget in self.frame_historico.winfo_children():
            widget.destroy()

        for item in historico[:9]:

            tecnico = item.get(
                "tecnico",
                "—",
            )

            numero_ticket = item.get(
                "numero_ticket",
                "—",
            )

            linha = tk.Label(
                self.frame_historico,
                text=f"{tecnico}  —  Ticket {numero_ticket}",
                bg=COR_FUNDO,
                fg=COR_TEXTO,
                font=(FONTE_PADRAO, 9),
                anchor="w",
            )

            linha.pack(
                fill="x",
                pady=1,
            )

    def alternar_fixacao(self):

        self.fixado = not self.fixado

        self.root.attributes(
            "-topmost",
            self.fixado,
        )

        if self.fixado:

            self.btn_fixar.config(
                text="📌  Fixado no topo"
            )

        else:

            self.btn_fixar.config(
                text="📍  Fixar no topo"
            )