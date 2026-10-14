import queue
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor

from src.fila_me.ui.estilos import FONTE_PADRAO


class ExecutorUI:
    """Nenhuma chamada Tk ocorre nas threads de rede/banco."""
    def __init__(self, root):
        self.root = root
        self.pool = ThreadPoolExecutor(max_workers=3, thread_name_prefix="fila-me")
        self.resultados = queue.Queue()
        self.ativo = True
        self.timer = root.after(100, self.processar)

    def executar(self, funcao, sucesso, falha):
        if not self.ativo:
            return
        futuro = self.pool.submit(funcao)
        futuro.add_done_callback(lambda f: self.resultados.put((f, sucesso, falha)))

    def processar(self):
        if not self.ativo:
            return
        while True:
            try:
                futuro, sucesso, falha = self.resultados.get_nowait()
            except queue.Empty:
                break
            try:
                resultado = futuro.result()
            except Exception as erro:
                falha(erro)
            else:
                sucesso(resultado)
        self.timer = self.root.after(100, self.processar)

    def encerrar(self):
        self.ativo = False
        self.root.after_cancel(self.timer)
        self.pool.shutdown(wait=False, cancel_futures=True)


class Tooltip:
    def __init__(self, widget, texto):
        self.widget, self.texto, self.janela = widget, texto, None
        widget.bind("<Enter>", self.mostrar, add="+")
        widget.bind("<Leave>", self.fechar, add="+")
        widget.bind("<Destroy>", self.fechar, add="+")

    def mostrar(self, evento=None):
        self.fechar()
        self.janela = tk.Toplevel(self.widget)
        self.janela.overrideredirect(True)
        self.janela.geometry(f"+{self.widget.winfo_rootx()}+{self.widget.winfo_rooty()+self.widget.winfo_height()+6}")
        tk.Label(self.janela, text=self.texto, bg="#11151C", fg="#FFFFFF",
                 padx=9, pady=6, font=(FONTE_PADRAO, 9)).pack()

    def fechar(self, evento=None):
        if self.janela:
            self.janela.destroy()
            self.janela = None


def botao(parent, texto, comando, cores, destaque=False, **kwargs):
    return tk.Button(parent, text=texto, command=comando,
                     bg=cores["azul"] if destaque else cores["botao"],
                     fg="#FFFFFF" if destaque else cores["texto"],
                     activebackground=cores["borda"], activeforeground=cores["texto"],
                     relief="flat", bd=0, padx=12, pady=8, cursor="hand2",
                     font=(FONTE_PADRAO, 10), **kwargs)


class BarraRolagem(tk.Canvas):
    """Trilho discreto, sem borda nativa clara, com arraste e clique."""
    def __init__(self,parent,canvas,cores):
        self.canvas_alvo,self.cores=canvas,cores
        self.inicio,self.fim=0.0,1.0
        self.arraste=None
        super().__init__(parent,width=9,highlightthickness=0,bg=cores["painel"],cursor="hand2")
        self.bind("<Configure>",lambda e:self.desenhar())
        self.bind("<Button-1>",self.pressionar)
        self.bind("<B1-Motion>",self.mover)
        self.bind("<ButtonRelease-1>",lambda e:setattr(self,"arraste",None))

    def set(self,inicio,fim):
        novo=(float(inicio),float(fim))
        if novo!=(self.inicio,self.fim):
            self.inicio,self.fim=novo
            self.desenhar()

    def desenhar(self):
        self.delete("all")
        altura=self.winfo_height()
        if self.fim-self.inicio >= .999 or altura<=1:
            return
        self.create_line(4,self.inicio*altura+3,4,max(self.inicio*altura+9,self.fim*altura-3),
                         width=5,capstyle="round",fill=self.cores["borda"])

    def pressionar(self,event):
        altura=max(1,self.winfo_height())
        if self.inicio*altura<=event.y<=self.fim*altura:
            self.arraste=event.y-self.inicio*altura
        else:
            self.canvas_alvo.yview_moveto(max(0,event.y/altura-(self.fim-self.inicio)/2))

    def mover(self,event):
        if self.arraste is not None:
            self.canvas_alvo.yview_moveto(max(0,(event.y-self.arraste)/max(1,self.winfo_height())))


class ListaRolavel(tk.Frame):
    def __init__(self,parent,cores,altura,passo=None):
        super().__init__(parent,bg=cores["painel"])
        self._delta=0
        self.passo=passo or round(28*fator_escala(parent))
        self.canvas=tk.Canvas(self,bg=cores["painel"],height=altura,highlightthickness=0,
                              yscrollincrement=self.passo)
        barra=BarraRolagem(self,self.canvas,cores)
        self.conteudo=tk.Frame(self.canvas,bg=cores["painel"])
        self.item=self.canvas.create_window((0,0),window=self.conteudo,anchor="nw")
        self.canvas.configure(yscrollcommand=barra.set)
        self.canvas.pack(side="left",fill="both",expand=True)
        barra.pack(side="right",fill="y",padx=(0,2))
        self.conteudo.bind("<Configure>",lambda e:self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",lambda e:self.canvas.itemconfigure(self.item,width=e.width))
        self.vincular_roda(self.canvas)
        self.vincular_roda(self.conteudo)

    def vincular_roda(self,widget):
        widget.bind("<MouseWheel>",self.rolar,add="+")
        widget.bind("<Button-4>",self.rolar,add="+")
        widget.bind("<Button-5>",self.rolar,add="+")
        for filho in widget.winfo_children():
            self.vincular_roda(filho)

    def rolar(self,event):
        numero=getattr(event,"num",None)
        if numero in (4,5):
            unidades=-1 if numero==4 else 1
        else:
            self._delta+=getattr(event,"delta",0)
            unidades=-int(self._delta/120)
            self._delta+=unidades*120
        if unidades:
            self.canvas.yview_scroll(unidades,"units")
        return "break"

    def limpar(self):
        for widget in self.conteudo.winfo_children():
            widget.destroy()


def fator_escala(root):
    # Tk usa fontes em pontos; os vetores acompanham o DPI da janela.
    return max(1.0, float(root.tk.call("tk", "scaling")) / (96 / 72))


def ajustar_tamanho(root, largura, altura, minimo=None):
    escala = fator_escala(root)
    minimo = minimo or (largura, altura)
    root.minsize(round(minimo[0]*escala), round(minimo[1]*escala))
    root.geometry(f"{round(largura*escala)}x{round(altura*escala)}")


class BotaoIcone(tk.Canvas):
    """Botão acessível por mouse, Tab, Enter e Espaço, com fundo arredondado."""
    def __init__(self, parent, icone, comando, cores, texto="", largura=42,
                 altura=38, cor=None, fundo=None, contador=False, sem_borda=False, compacto=False):
        from src.fila_me.ui.icones import carregar_icone
        self._carregar_icone = carregar_icone
        self.icone, self.comando, self.cores = icone, comando, cores
        self.texto = texto
        self.cor = cor or cores["texto"]
        self.fundo = fundo or cores["botao"]
        self.contador = contador
        self.sem_borda = sem_borda
        self.compacto = compacto
        self.escala = fator_escala(parent)
        self.largura, self.altura = largura*self.escala, altura*self.escala
        self.foco = self.hover = self.selecionado = False
        super().__init__(parent, width=round(self.largura), height=round(self.altura),
                         bg=cores["fundo"], highlightthickness=0, takefocus=True, cursor="hand2")
        self.bind("<Configure>", self.redimensionar)
        self.bind("<Button-1>", self.acionar)
        self.bind("<Return>", self.acionar)
        self.bind("<space>", self.acionar)
        self.bind("<FocusIn>", lambda e: self.marcar_foco(True))
        self.bind("<FocusOut>", lambda e: self.marcar_foco(False))
        self.bind("<Enter>", lambda e: self.marcar_hover(True))
        self.bind("<Leave>", lambda e: self.marcar_hover(False))
        self.redesenhar()

    def redimensionar(self, evento):
        self.largura,self.altura=evento.width,evento.height
        self.redesenhar()

    def acionar(self, evento=None):
        self.focus_set()
        self.comando()
        return "break"

    def marcar_foco(self, valor):
        self.foco = valor
        self.redesenhar()

    def marcar_hover(self, valor):
        self.hover = valor
        self.redesenhar()

    def configure(self, cnf=None, **kwargs):
        if cnf:
            kwargs.update(cnf)
        alterado=False
        for atributo, opcao in (("texto", "text"), ("cor", "fg"), ("fundo", "fundo"), ("selecionado", "selecionado"), ("icone", "icone")):
            if opcao in kwargs:
                valor=kwargs.pop(opcao)
                if getattr(self,atributo)!=valor:
                    setattr(self,atributo,valor)
                    alterado=True
        if kwargs:
            super().configure(**kwargs)
            alterado=True
        if alterado and hasattr(self,"_carregar_icone"):
            self.redesenhar()
    config = configure

    def redesenhar(self):
        self.delete("all")
        w,h,s=self.largura,self.altura,self.escala
        r=8*s
        borda=self.cor if self.selecionado else self.cores["borda"] if self.hover or self.foco else self.fundo
        if getattr(self, 'sem_borda', False):
            borda = ""
        self.create_polygon(1+r,1,w-r-1,1,w-1,1,w-1,r+1,w-1,h-r-1,w-1,h-1,
                            w-r-1,h-1,r+1,h-1,1,h-1,1,h-r-1,1,r+1,1,1,
                            smooth=True, fill=self.fundo, outline=borda, width=1.5*s)
        compacto = getattr(self, 'compacto', False)
        tamanho=(16 if compacto else 18)*s
        if self.contador:
            self.create_oval(11*s,h/2-3*s,17*s,h/2+3*s,fill=self.cor,outline="")
            self.create_text(32*s,h/2,text=self.texto,fill=self.cor,font=(FONTE_PADRAO,10,"bold"))
            ix=w-31*s
        elif self.texto:
            ix=(7 if compacto else 12)*s
            self.create_text((29 if compacto else 42)*s,h/2,text=self.texto,fill=self.cor,anchor="w",font=(FONTE_PADRAO,9))
        else:
            ix=(w-tamanho)/2
        self._icone_img=self._carregar_icone(self.icone,round(tamanho),self.cor,self._root())
        self.create_image(ix+tamanho/2,h/2,image=self._icone_img)


class SeletorCargo(tk.Frame):
    """Duas opções exclusivas, com realce da seleção e ícones PNG."""
    def __init__(self, parent, cores, cor):
        super().__init__(parent, bg=cores["fundo"])
        self.cores, self.cor, self.valor = cores, cor, None
        self.opcoes = {}
        for valor, icone in (("Técnico", "tecnico"), ("Supervisão", "supervisao")):
            b=BotaoIcone(self,icone,lambda v=valor:self.selecionar(v),cores,
                         texto=valor,largura=150,altura=36)
            b.pack(side="left",expand=True,fill="x",padx=(0,5) if valor=="Técnico" else (5,0))
            self.opcoes[valor]=b
        self.redesenhar()

    def get(self):
        return self.valor

    def selecionar(self, valor):
        self.valor=valor
        self.redesenhar()

    def atualizar_cor(self, cor):
        self.cor=cor
        self.redesenhar()

    def redesenhar(self):
        for valor,b in self.opcoes.items():
            b.configure(fg=self.cor if valor==self.valor else self.cores["secundario"],
                        fundo=self.cores["painel"] if valor==self.valor else self.cores["botao"])
            b.configure(selecionado=valor==self.valor)


def escolher_paleta(root, cores, cor_atual, ao_escolher):
    from src.fila_me.config import preferencias
    from src.fila_me.ui.estilos import cor_destaque
    janela=tk.Toplevel(root)
    janela.title("Escolher cor")
    janela.configure(bg=cores["fundo"])
    janela.resizable(False,False)
    janela.transient(root)
    tk.Label(janela,text="Cor de destaque",bg=cores["fundo"],fg=cores["texto"],
             font=(FONTE_PADRAO,12,"bold")).pack(padx=22,pady=(18,10))
    opcoes=tk.Frame(janela,bg=cores["fundo"])
    opcoes.pack(padx=14)
    for indice,(nome,valor) in enumerate(preferencias.PALETA.items()):
        def escolher(cor=valor):
            janela.destroy()
            ao_escolher(cor)
        b=BotaoIcone(opcoes,"paleta",escolher,cores,texto=nome,largura=132,altura=32,
                     cor=cor_destaque(valor,"claro" if cores["fundo"]=="#F4F6FA" else "escuro"))
        b.grid(row=indice//3,column=indice%3,padx=3,pady=3)
        if valor==cor_atual:
            b.configure(selecionado=True)
    tk.Label(janela,text="Verde é reservado ao bloqueio confirmado.",bg=cores["fundo"],
             fg=cores["secundario"],font=(FONTE_PADRAO,9)).pack(padx=18,pady=(12,18))
    janela.bind("<Escape>", lambda e: janela.destroy())
    janela.grab_set()
