import tkinter as tk
from tkinter import messagebox

from src.fila_me.database.autenticacao import cadastrar_usuario
from src.fila_me.ui.componentes import (botao, SeletorCargo, ajustar_tamanho)
from src.fila_me.ui.estilos import TEMAS, FONTE_PADRAO, cor_destaque, cor_texto_botao


class TelaCadastro:
    def __init__(self, root, ao_voltar, executor, aparencia=None):
        self.root, self.ao_voltar, self.executor = root, ao_voltar, executor
        self.aparencia = aparencia or {"tema": "escuro", "cor": "#FF626B"}
        self.ativo = True
        self.c = TEMAS[self.aparencia["tema"]]
        root.title("Fila ME • Criar cadastro")
        ajustar_tamanho(root, 390, 560, (370, 550))
        root.configure(bg=self.c["fundo"])
        root.resizable(True, True)
        self.frame = tk.Frame(root, bg=self.c["fundo"])
        self.frame.pack(fill="both", expand=True, padx=26, pady=18)
        self.label("Fila ME", 22, True).pack(pady=(0, 5))
        self.label("Criar cadastro", 10).pack(pady=(0, 8))
        self.nome = self.campo("Nome completo")
        self.email = self.campo("E-mail")
        self.senha = self.campo("Senha", True)
        self.confirmacao = self.campo("Confirmar senha", True)
        self.label("Cargo", 9).pack(anchor="w", pady=(8, 5))
        self.cargo = SeletorCargo(self.frame, self.c, cor_destaque(self.aparencia["cor"], self.aparencia["tema"]))
        self.cargo.pack(fill="x")
        self.cadastrar_btn = botao(self.frame, "Criar cadastro", self.cadastrar, self.c, destaque=True)
        self.cadastrar_btn.pack(fill="x", pady=(14, 6))
        botao(self.frame, "Voltar para login", ao_voltar, self.c).pack(fill="x")
        self.aplicar_cor()

    def label(self, texto, tamanho=10, bold=False):
        return tk.Label(self.frame, text=texto, bg=self.c["fundo"],
                        fg=self.c["texto"] if bold else self.c["secundario"],
                        font=(FONTE_PADRAO, tamanho, "bold" if bold else "normal"))

    def campo(self, texto, senha=False):
        self.label(texto, 9).pack(anchor="w", pady=(7, 3))
        e = tk.Entry(self.frame, show="•" if senha else "", bg=self.c["campo"], fg=self.c["texto"],
                     insertbackground=self.c["texto"], relief="flat", font=(FONTE_PADRAO, 10),
                     highlightthickness=1, highlightbackground=self.c["borda"], highlightcolor=self.c["azul"])
        e.pack(fill="x", ipady=4)
        return e

    def aplicar_cor(self):
        cor=cor_destaque(self.aparencia["cor"],self.aparencia["tema"])
        self.cadastrar_btn.configure(bg=cor,fg=cor_texto_botao(cor),activebackground=cor,
                                     activeforeground=cor_texto_botao(cor))
        self.cargo.atualizar_cor(cor)
        for campo in (self.nome,self.email,self.senha,self.confirmacao):
            campo.configure(highlightcolor=cor)

    def cadastrar(self):
        if not self.ativo or str(self.cadastrar_btn["state"]) == "disabled":
            return
        try:
            nome, email, senha = self.nome.get().strip(), self.email.get().strip(), self.senha.get()
            if not nome or not email or not senha:
                raise ValueError("Preencha todos os campos.")
            if senha != self.confirmacao.get():
                raise ValueError("As senhas não coincidem.")
            if self.cargo.get() is None:
                raise ValueError("Selecione o cargo.")
        except ValueError as erro:
            messagebox.showwarning("Cadastro", str(erro))
            return
        cargo = "tecnico" if self.cargo.get() == "Técnico" else "supervisao"
        self.cadastrar_btn.configure(state="disabled", text="Cadastrando…")
        self.executor.executar(lambda: cadastrar_usuario(nome, email, senha, cargo), self.sucesso, self.erro)

    def sucesso(self, resultado):
        if self.ativo:
            messagebox.showinfo("Cadastro", "Cadastro criado. Agora você pode entrar.")
            self.ao_voltar()

    def erro(self, erro):
        if self.ativo:
            self.cadastrar_btn.configure(state="normal", text="Criar cadastro")
            mensagem = "E-mail já cadastrado." if getattr(erro, "sqlstate", None) == "23505" else "Não foi possível cadastrar. Verifique a conexão e tente novamente."
            messagebox.showerror("Cadastro", mensagem)

    def encerrar(self):
        self.ativo = False
        self.frame.destroy()
