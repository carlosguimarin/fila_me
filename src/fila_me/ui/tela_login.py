import tkinter as tk
from tkinter import messagebox

from src.fila_me.database.autenticacao import autenticar_usuario
from src.fila_me.ui.componentes import botao, ajustar_tamanho
from src.fila_me.ui.estilos import TEMAS, FONTE_PADRAO, cor_destaque, cor_texto_botao


class TelaLogin:
    def __init__(self, root, ao_logar, ao_cadastrar, executor, aparencia=None):
        self.root, self.ao_logar, self.executor = root, ao_logar, executor
        self.aparencia = aparencia or {"tema": "escuro", "cor": "#FF626B"}
        self.ativo = True
        self.c = TEMAS[self.aparencia["tema"]]
        root.title("Fila ME • Entrar")
        ajustar_tamanho(root, 360, 360, (340, 350))
        root.resizable(True, True)
        root.configure(bg=self.c["fundo"])
        self.frame = tk.Frame(root, bg=self.c["fundo"])
        self.frame.pack(fill="both", expand=True, padx=30, pady=24)
        self.label("Fila ME", 24, True).pack(pady=(0, 18))
        self.identificacao_entry = self.campo("Login")
        self.senha_entry = self.campo("Senha", senha=True)
        self.entrar_btn = botao(self.frame, "Entrar", self.entrar, self.c, destaque=True)
        self.entrar_btn.pack(fill="x", pady=(16, 8))
        self.cadastro_btn = botao(self.frame, "Criar cadastro", ao_cadastrar, self.c)
        self.cadastro_btn.pack(fill="x")
        self.aplicar_cor()
        self.identificacao_entry.focus_set()
        self.identificacao_entry.bind("<Return>", self.ir_para_senha)
        self.senha_entry.bind("<Return>", lambda e: self.entrar())

    def ir_para_senha(self, evento=None):
        self.senha_entry.focus_set()
        return "break"

    def label(self, texto, tamanho=10, bold=False):
        return tk.Label(self.frame, text=texto, bg=self.c["fundo"],
                        fg=self.c["texto"] if bold else self.c["secundario"],
                        font=(FONTE_PADRAO, tamanho, "bold" if bold else "normal"))

    def campo(self, texto, senha=False):
        self.label(texto, 9).pack(anchor="w", pady=(8, 4))
        entry = tk.Entry(self.frame, show="•" if senha else "", bg=self.c["campo"],
                         fg=self.c["texto"], insertbackground=self.c["texto"], relief="flat",
                         highlightthickness=1, highlightbackground=self.c["borda"],
                         highlightcolor=self.c["azul"], font=(FONTE_PADRAO, 11))
        entry.pack(fill="x", ipady=6)
        return entry

    def aplicar_cor(self):
        cor = cor_destaque(self.aparencia["cor"], self.aparencia["tema"])
        self.entrar_btn.configure(bg=cor, fg=cor_texto_botao(cor), activebackground=cor,
                                  activeforeground=cor_texto_botao(cor))
        self.cadastro_btn.configure(fg=cor, activeforeground=cor)
        for campo in (self.identificacao_entry, self.senha_entry):
            campo.configure(highlightcolor=cor)

    def entrar(self):
        if not self.ativo or str(self.entrar_btn["state"]) == "disabled":
            return
        identificacao, senha = self.identificacao_entry.get().strip(), self.senha_entry.get()
        if not identificacao or not senha:
            messagebox.showwarning("Login", "Informe o login e a senha.")
            return
        self.entrar_btn.configure(state="disabled", text="Entrando…")
        self.executor.executar(lambda: autenticar_usuario(identificacao, senha), self.receber_login, self.erro)

    def receber_login(self, usuario):
        if not self.ativo:
            return
        self.entrar_btn.configure(state="normal", text="Entrar")
        if usuario is None:
            messagebox.showerror("Login", "Login ou senha inválidos, ou usuário inativo.")
        else:
            self.ao_logar(usuario)

    def erro(self, erro):
        if self.ativo:
            self.entrar_btn.configure(state="normal", text="Entrar")
            messagebox.showerror("Conexão", "Não foi possível entrar. Verifique a conexão e a configuração do banco.")

    def encerrar(self):
        self.ativo = False
        self.frame.destroy()
