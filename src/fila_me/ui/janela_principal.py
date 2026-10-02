import tkinter as tk

from src.fila_me.config.settings import (
    NOME_APLICACAO,
    LARGURA_JANELA,
    ALTURA_JANELA,
)

from src.fila_me.models.fila import Fila

from src.fila_me.ui.estilos import (
    COR_FUNDO,
    COR_PAINEL,
    COR_TEXTO,
    COR_SECUNDARIO,
    COR_DESTAQUE,
    COR_DESTAQUE_HOVER,
    COR_BOTAO,
    FONTE_PADRAO,
)


class JanelaPrincipal:
    def __init__(self, root, fila):
        self.root = root
        self.fila = fila
        self.fixado = True

        self.configurar_janela()
        self.criar_interface()

    def configurar_janela(self):
        self.root.title(NOME_APLICACAO)

        self.root.geometry(
            f"{LARGURA_JANELA}x{ALTURA_JANELA}"
        )

        self.root.resizable(False, False)
        self.root.configure(bg=COR_FUNDO)

        # Mantém a janela sempre sobre as outras.
        self.root.attributes("-topmost", True)

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

        titulo.pack(pady=(16, 2))

        # -------------------------
        # SUBTÍTULO
        # -------------------------

        subtitulo = tk.Label(
            self.root,
            text="É a vez de",
            bg=COR_FUNDO,
            fg=COR_SECUNDARIO,
            font=(FONTE_PADRAO, 9),
        )

        subtitulo.pack()

        # -------------------------
        # NOME
        # -------------------------

        self.nome_label = tk.Label(
            self.root,
            text=self.fila.tecnico_atual,
            bg=COR_FUNDO,
            fg=COR_TEXTO,
            font=(FONTE_PADRAO, 27, "bold"),
        )

        self.nome_label.pack(pady=(0, 8))

        # -------------------------
        # BOTÕES
        # -------------------------

        frame_botoes = tk.Frame(
            self.root,
            bg=COR_FUNDO,
        )

        frame_botoes.pack()

        self.btn_anterior = tk.Button(
            frame_botoes,
            text="‹  Anterior",
            command=self.anterior,
            width=12,
            bg=COR_BOTAO,
            fg=COR_TEXTO,
            activebackground="#45474C",
            activeforeground=COR_TEXTO,
            relief="flat",
            bd=0,
            font=(FONTE_PADRAO, 9, "bold"),
            cursor="hand2",
        )

        self.btn_anterior.pack(
            side="left",
            padx=4,
        )

        self.btn_proximo = tk.Button(
            frame_botoes,
            text="Próximo  ›",
            command=self.proximo,
            width=12,
            bg=COR_DESTAQUE,
            fg="white",
            activebackground=COR_DESTAQUE_HOVER,
            activeforeground="white",
            relief="flat",
            bd=0,
            font=(FONTE_PADRAO, 9, "bold"),
            cursor="hand2",
        )

        self.btn_proximo.pack(
            side="left",
            padx=4,
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

        self.btn_fixar.pack(pady=(9, 0))

    def atualizar_nome(self):
        self.nome_label.config(
            text=self.fila.tecnico_atual
        )

    def proximo(self):
        self.fila.proximo()
        self.atualizar_nome()

    def anterior(self):
        self.fila.anterior()
        self.atualizar_nome()

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