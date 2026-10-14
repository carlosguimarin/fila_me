import tkinter as tk
import webbrowser
from datetime import datetime
from tkinter import messagebox

from src.fila_me.config import preferencias
from src.fila_me.database.banco import (
    atualizar_heartbeat,
    atualizar_status_trabalhando,
    buscar_painel_visual,
)
from src.fila_me.ui.componentes import ListaRolavel, Tooltip, BotaoIcone, ajustar_tamanho, fator_escala
from src.fila_me.ui.menus import MenuSuspenso
from src.fila_me.ui.estilos import FONTE_PADRAO, TEMAS, cor_destaque, nome_curto


class JanelaPrincipal:
    def __init__(self, root, usuario, ao_sair, executor, aparencia=None):
        self.root, self.usuario, self.ao_sair, self.executor = root, usuario, ao_sair, executor
        self.prefs = preferencias.normalizar(aparencia) if aparencia is not None else preferencias.carregar(usuario["id"])
        self.ativo, self.sempre_no_topo, self.em_consulta = True, False, False
        self.timer = None
        self.heartbeat_timer = None
        self.copia_timer = None
        self._filtro_dados = self.prefs["filtro"]
        self.dados = {"proximo": "Carregando…", "historico": [], "online": []}
        self.ultima_atualizacao = None
        self.estado_conexao = "Conectando…"
        self.popup_online = None
        if self.usuario["cargo"] == "tecnico":
            atualizar_status_trabalhando(self.usuario["id"], True)
            self.enviar_heartbeat()
        self.criar_interface()
        self.atualizar_estado()

    def criar_interface(self):
        self.cancelar_aviso_copia()
        self.fechar_menu_ticket()
        self.encerrar_menus()
        if hasattr(self, "frame"):
            self.frame.destroy()
        self.c = TEMAS[self.prefs["tema"]]
        self.cor = cor_destaque(self.prefs["cor"], self.prefs["tema"])
        compacto = self.prefs["modo"] == "simples"
        self.root.title("Fila ME")
        self.root.resizable(True, True)
        if getattr(self, "_modo_renderizado", None) != self.prefs["modo"]:
            ajustar_tamanho(self.root, 300 if compacto else 350, 330 if compacto else 390,
                            (280,280) if compacto else (330,330))
        self._modo_renderizado = self.prefs["modo"]
        self._assinatura_historico = None
        self._widgets_historico = {}
        self._placeholder_historico = None
        self.root.configure(bg=self.c["fundo"])
        self.frame = tk.Frame(self.root, bg=self.c["fundo"])
        self.frame.pack(fill="both", expand=True, padx=7,pady=6)
        topo = tk.Frame(self.frame, bg=self.c["fundo"])
        topo.pack(fill="x")
        info = tk.Frame(topo, bg=self.c["fundo"])
        info.pack(side="left", padx=(0, 8))
        self.label(info, nome_curto(self.usuario["nome"]), 9, bold=True).pack(anchor="w")
        self.label(info, "Técnico" if self.usuario["cargo"] == "tecnico" else "Supervisão", 8, secundario=True).pack(anchor="w")
        acoes = tk.Frame(topo, bg=self.c["fundo"])
        acoes.pack(side="right")
        self.fixar = BotaoIcone(acoes,"fixar",self.alternar_topo,self.c,cor=self.c["coral"],largura=28,altura=28,
                               sem_borda=True)
        self.fixar.pack(side="left",padx=2)
        Tooltip(self.fixar,"Fixar ou desafixar a janela")
        self.online = BotaoIcone(acoes,"usuarios",self.mostrar_online,self.c,texto="0",largura=54,altura=28,
                                cor=self.c["verde"],fundo="#25362E" if self.prefs["tema"]=="escuro" else "#E7F2EB",
                                contador=False, compacto=True)
        self.online.pack(side="left",padx=2)
        self.preferencias_botao = BotaoIcone(acoes,"preferencias",self.mostrar_preferencias,self.c,largura=28,altura=28)
        self.preferencias_botao.pack(side="left",padx=2)
        sair = BotaoIcone(acoes,"sair",self.ao_sair,self.c,cor=self.c["coral"],fundo=self.c["saida"],largura=28,altura=28)
        sair.pack(side="left",padx=2)
        self.menus = []
        self.menu_preferencias = MenuSuspenso(self.root, self.preferencias_botao,
            self.construir_preferencias, self.fechar_outros_menus, self.c["fundo"], self.c["borda"])
        self.menu_online = MenuSuspenso(self.root, self.online,
            self.construir_online, self.fechar_outros_menus, self.c["fundo"], self.c["borda"])
        self.menus = [self.menu_preferencias, self.menu_online]
        self.proximo = self.label(self.frame, "Próximo: carregando…", 11 if compacto else 12, bold=True)
        self.proximo.configure(fg=self.cor)
        self.proximo.pack(pady=(7,5))
        self.label(self.frame, "Últimas atribuições", 9, bold=True, secundario=True).pack(anchor="w", pady=(2, 4))
        self.altura_linha=round((24 if compacto else 36)*fator_escala(self.root))
        self.historico = ListaRolavel(self.frame,self.c,170 if compacto else 230,passo=self.altura_linha)
        self.conexao = self.label(self.frame, "Conectando…", 8, secundario=True)
        self.conexao.pack(side="bottom")
        self.historico.pack(fill="both",expand=True)
        self.renderizar()

    def label(self, parent, texto, tamanho=10, bold=False, secundario=False):
        return tk.Label(parent, text=texto, bg=self.c["fundo"],
                        fg=self.c["secundario"] if secundario else self.c["texto"],
                        font=(FONTE_PADRAO, tamanho, "bold" if bold else "normal"))

    def alternar_topo(self):
        self.sempre_no_topo = not self.sempre_no_topo
        self.root.attributes("-topmost", self.sempre_no_topo)
        for menu in getattr(self, 'menus', []):
            menu.sincronizar_topo()
        self.fixar.configure(fg=self.c["coral"],selecionado=self.sempre_no_topo,
                             icone="fixado" if self.sempre_no_topo else "fixar")

    def guardar_preferencias(self):
        try:
            preferencias.salvar(self.usuario["id"], self.prefs)
        except OSError:
            messagebox.showwarning("Preferências", "A mudança foi aplicada, mas não foi possível salvá-la neste computador.")
        if self.popup_online and self.popup_online.winfo_exists():
            self.popup_online.destroy()
        self.criar_interface()
        self.root.attributes("-topmost", self.sempre_no_topo)
        self.fixar.configure(fg=self.c["coral"],selecionado=self.sempre_no_topo,
                             icone="fixado" if self.sempre_no_topo else "fixar")

    def alternar_modo(self):
        self.prefs["modo"] = "avancado" if self.prefs["modo"] == "simples" else "simples"
        self.guardar_preferencias()

    def alternar_tema(self):
        self.prefs["tema"] = "claro" if self.prefs["tema"] == "escuro" else "escuro"
        self.guardar_preferencias()

    def encerrar_menus(self):
        for menu in getattr(self, "menus", []):
            menu.encerrar()
        self.menus = []
        self.popup_online = None

    def fechar_outros_menus(self, atual):
        for menu in self.menus:
            if menu is not atual:
                menu.fechar()

    def mostrar_preferencias(self):
        self.menu_preferencias.alternar()

    def selecionar_preferencia(self, chave, valor):
        if self.prefs[chave] != valor:
            self.prefs[chave] = valor
            self.guardar_preferencias()
            if chave == "filtro":
                self.consultar_estado()

    def construir_preferencias(self, popup):
        corpo = tk.Frame(popup, bg=self.c["fundo"])
        corpo.pack(padx=10, pady=8)
        for chave, titulo, opcoes in (
            ("modo", "Visualização", (("simples", "Simples"), ("avancado", "Avançado"))),
            ("tema", "Tema", (("escuro", "Escuro"), ("claro", "Claro"))),
            ("filtro", "Filtro", (("todos", "Todos"), ("meus", "Atribuídos a mim")))):
            linha = tk.Frame(corpo, bg=self.c["fundo"])
            linha.pack(fill="x", pady=3)
            self.label(linha, titulo, 8, secundario=True).pack(side="left", padx=(0, 8))
            for valor, texto in opcoes:
                selecionado = self.prefs[chave] == valor
                tk.Button(linha, text=texto, command=lambda c=chave, v=valor: self.selecionar_preferencia(c, v),
                          font=(FONTE_PADRAO, 8, "bold" if selecionado else "normal"),
                          bg=self.c["botao"] if selecionado else self.c["fundo"],
                          fg=self.cor if selecionado else self.c["secundario"],
                          activebackground=self.c["botao"], activeforeground=self.c["texto"],
                          relief="flat", borderwidth=0, padx=5, pady=4).pack(side="left", padx=1)
        self.label(corpo, "Cor de destaque", 8, secundario=True).pack(anchor="w", pady=(6, 3))
        grade = tk.Frame(corpo, bg=self.c["fundo"])
        grade.pack(anchor="w")
        escala = fator_escala(self.root)
        for i, (nome, cor) in enumerate(preferencias.PALETA.items()):
            amostra = tk.Canvas(grade, width=round(30*escala), height=round(24*escala),
                                bg=self.c["fundo"], highlightthickness=0, takefocus=True, cursor="hand2")
            amostra.create_oval(5*escala, 3*escala, 23*escala, 21*escala,
                               fill=cor_destaque(cor, self.prefs["tema"]), outline="")
            if self.prefs["cor"] == cor:
                amostra.create_oval(9*escala, 7*escala, 19*escala, 17*escala,
                                   outline=self.c["texto"], width=2*escala)
            amostra.grid(row=i//6, column=i%6, padx=1, pady=1)
            for evento in ("<Button-1>", "<Return>", "<space>"):
                amostra.bind(evento, lambda e, v=cor: self.selecionar_preferencia("cor", v))
            amostra.bind("<FocusIn>", lambda e: e.widget.configure(highlightthickness=1, highlightbackground=self.c["texto"]))
            amostra.bind("<FocusOut>", lambda e: e.widget.configure(highlightthickness=0))
            Tooltip(amostra, nome)

    def mostrar_online(self):
        self.menu_online.alternar()

    def construir_online(self, popup):
        self.popup_online = popup
        self.label(popup, "Online", 10, bold=True).pack(anchor="w", padx=12, pady=(8, 0))
        self.lista_online = ListaRolavel(popup, self.c, 60)
        self.lista_online.canvas.configure(width=round(205*fator_escala(self.root)))
        self.lista_online.pack(fill="both", expand=True, padx=5, pady=5)
        self._assinatura_online = None
        self.renderizar_online()

    def renderizar_online(self):
        if not self.popup_online or not self.popup_online.winfo_exists():
            return
        assinatura=tuple(tuple(u.get(k) for k in ("id","nome","cargo","trabalhando"))
                         for u in self.dados["online"])
        if assinatura==self._assinatura_online:
            return
        self._assinatura_online=assinatura
        self.lista_online.limpar()
        linhas = 0
        for cargo, titulo in (("tecnico", "Técnicos"),):
            pessoas = [u for u in self.dados["online"] if u["cargo"] == cargo and (cargo != "tecnico" or u["trabalhando"])]
            if not pessoas:
                continue
            self.label(self.lista_online.conteudo, f"{titulo} · {len(pessoas)}", 8, secundario=True).pack(anchor="w", padx=7, pady=(5, 2))
            linhas += 1
            for u in pessoas:
                l = self.label(self.lista_online.conteudo, nome_curto(u["nome"]), 9)
                l.pack(anchor="w", padx=7, pady=2)
                self.lista_online.vincular_roda(l)
                linhas += 1
        if not linhas:
            self.label(self.lista_online.conteudo, "Ninguém online", 9, secundario=True).pack(padx=7, pady=8)
        self.lista_online.canvas.configure(height=round(min(180, max(40, linhas*24))*fator_escala(self.root)))

    def consultar_estado(self):
        if self.ativo and not self.em_consulta:
            self.em_consulta = True
            filtro = self.prefs.get("filtro", "todos")
            self.executor.executar(lambda: buscar_painel_visual(self.usuario, filtro=filtro),
                                  lambda dados: self.receber_estado_filtrado(dados, filtro), self.erro_estado)

    def receber_estado_filtrado(self, dados, filtro):
        self.em_consulta = False
        if not self.ativo:
            return
        if filtro != self.prefs.get("filtro", "todos"):
            self.consultar_estado()
            return
        self._filtro_dados = filtro
        self.receber_estado(dados)

    def atualizar_estado(self):
        if not self.ativo:
            return
        self.consultar_estado()
        self.timer = self.root.after(5000, self.atualizar_estado)

    def receber_estado(self, dados):
        self.em_consulta = False
        if not self.ativo:
            return
        self.dados = dados
        self.ultima_atualizacao = datetime.now().strftime("%H:%M:%S")
        self.estado_conexao = f"Atualizado às {self.ultima_atualizacao}"
        self.renderizar()

    def erro_estado(self, erro):
        self.em_consulta = False
        if self.ativo:
            self.estado_conexao = "Sem conexão • dados podem estar desatualizados"
            self.renderizar()

    def renderizar(self):
        proximo = self.dados["proximo"]
        self.proximo.configure(text="Próximo: " + (proximo if proximo in ("Nenhum técnico", "Carregando…") else nome_curto(proximo)))
        quantidade = sum(u["cargo"] == "tecnico" and u["trabalhando"] for u in self.dados["online"])
        desatualizado = self.estado_conexao.startswith("Sem conexão")
        self.online.configure(text="?" if desatualizado else str(quantidade),
                              fg=self.c["secundario"] if desatualizado else self.c["verde"])
        if not getattr(self, "copia_timer", None):
            self.conexao.configure(text=self.estado_conexao)
        carregando = getattr(self, "_filtro_dados", self.prefs.get("filtro", "todos")) != self.prefs.get("filtro", "todos")
        linhas=[] if carregando else self.dados["historico"]
        assinatura=(carregando, self.prefs.get("filtro", "todos"), tuple(tuple(a.get(k) for k in (
            "numero_ticket","tecnico","status","tipo_atribuicao","owner_otrs","atribuido_em",
            "meu","status_bloqueio","bloqueio_confirmado")) for a in linhas))
        if assinatura!=self._assinatura_historico and not carregando:
            self.sincronizar_historico(linhas)
            self._assinatura_historico=assinatura
        self.renderizar_online()

    def dados_apresentacao_historico(self, atribuicao):
        if atribuicao["tipo_atribuicao"] == "SUPERVISAO":
            login = "Supervisão"
        else:
            login = nome_curto(atribuicao["tecnico"]) or "Aguardando técnico"
        propria = self.atribuicao_do_usuario(atribuicao)
        assinatura = tuple(atribuicao.get(chave) for chave in (
            "numero_ticket", "tecnico", "status", "tipo_atribuicao", "owner_otrs",
            "atribuido_em", "status_bloqueio", "bloqueio_confirmado",
        )) + (login, propria)
        return login, propria, assinatura

    def sincronizar_historico(self, linhas):
        posicao = self.historico.posicao_vertical()
        chaves = {a["numero_ticket"] for a in linhas}
        alterado = False
        nova_atribuicao = any(
            atribuicao["numero_ticket"] not in self._widgets_historico
            for atribuicao in linhas
        )

        # Reordene a lista usando exatamente a ordem retornada pelo banco.
        # Inserir widgets antes de filhos existentes pode preservar uma ordem
        # antiga do Pack/Tk quando chegam novas atribuições.
        if nova_atribuicao:
            for item in self._widgets_historico.values():
                item["widget"].destroy()
            self._widgets_historico.clear()
            alterado = True

        for chave in tuple(self._widgets_historico):
            if chave not in chaves:
                self._widgets_historico.pop(chave)["widget"].destroy()
                alterado = True

        if not linhas:
            texto = (
                "Nenhuma atribuição para você."
                if self.prefs.get("filtro") == "meus"
                else "Nenhuma atribuição registrada."
            )
            if self._placeholder_historico is None:
                self._placeholder_historico = self.label(
                    self.historico.conteudo, texto, 10, secundario=True
                )
                self._placeholder_historico.pack(padx=14, pady=22, anchor="w")
                alterado = True
            elif self._placeholder_historico.cget("text") != texto:
                self._placeholder_historico.configure(text=texto)
                alterado = True
            if alterado:
                self.historico.restaurar_posicao_vertical(posicao)
            return

        if self._placeholder_historico is not None:
            self._placeholder_historico.destroy()
            self._placeholder_historico = None
            alterado = True

        # Na chegada de uma atribuição nova, recriamos apenas as linhas
        # recentes devolvidas pelo painel, já na ordem do banco (mais recente primeiro).
        for atribuicao in (linhas if nova_atribuicao else reversed(linhas)):
            chave = atribuicao["numero_ticket"]
            login, propria, assinatura_linha = self.dados_apresentacao_historico(atribuicao)
            item = self._widgets_historico.get(chave)
            if item is None:
                row = self.linha(
                    self.historico.conteudo,
                    chave,
                    login,
                    atribuicao,
                    propria,
                )
                self.historico.vincular_roda(row)
                self._widgets_historico[chave] = {
                    "widget": row,
                    "assinatura": assinatura_linha,
                }
                alterado = True
            elif item["assinatura"] != assinatura_linha:
                self.atualizar_linha(item["widget"], chave, login, atribuicao, propria)
                item["assinatura"] = assinatura_linha
                alterado = True

        if alterado:
            # Registros novos ficam no topo e devem ficar visíveis imediatamente.
            self.historico.restaurar_posicao_vertical(
                0 if nova_atribuicao else posicao
            )

    def vazio(self, lista, texto):
        self.label(lista.conteudo, texto, 10, secundario=True).pack(padx=14, pady=22, anchor="w")

    def atribuicao_do_usuario(self, dados):
        nome_usuario = self.usuario["nome"].casefold()
        if self.usuario["cargo"] == "supervisao":
            return (
                dados["tipo_atribuicao"] == "SUPERVISAO"
                and str(dados.get("owner_otrs") or "").casefold() == nome_usuario
            )
        return (
            dados["tipo_atribuicao"] != "SUPERVISAO"
            and str(dados.get("tecnico") or "").casefold() == nome_usuario
        )

    def linha(self, parent, numero, login, dados=None, propria=False, before=None):
        tamanho_texto = 8 if self.prefs["modo"] == "simples" else 9
        row=tk.Frame(parent,bg=self.c["painel"],height=self.altura_linha)
        if before is None:
            row.pack(fill="x",padx=5)
        else:
            row.pack(fill="x",padx=5,before=before)
        row.pack_propagate(False)
        conteudo = tk.Frame(row, bg=self.c["painel"])
        conteudo.pack(fill="x",expand=True)
        texto = tk.Frame(conteudo, bg=self.c["painel"])
        texto.pack(fill="x")
        row.texto = texto
        link = tk.Label(texto, text=f"#{numero}", bg=self.c["painel"],
                        fg=self.cor if propria else self.c["secundario"],
                        font=(FONTE_PADRAO,tamanho_texto),cursor="hand2", anchor="w")
        link.pack(side="left")
        link.bind("<Button-1>", lambda e: self.copiar_ticket(numero))
        link.bind("<Button-3>", lambda e: self.menu_ticket(e, numero, None))
        row.link_ticket = link
        nome_login = tk.Label(
            texto,
            text=login,
            bg=self.c["painel"],
            fg=self.cor if propria else self.c["secundario"],
            font=(FONTE_PADRAO, tamanho_texto),
        )
        nome_login.pack(side="left", padx=(7, 0))
        row.nome_login = nome_login
        row.cadeado = self.cadeado(
            texto,
            bool(dados and dados.get("bloqueio_confirmado")),
        )
        row.bloqueado = bool(dados and dados.get("bloqueio_confirmado"))
        row.detalhe = None
        if self.prefs["modo"] == "avancado":
            detalhe = dados['status'].replace('_', ' ').capitalize()
            if dados.get("atribuido_em"):
                detalhe += " • " + dados["atribuido_em"].strftime("%d/%m %H:%M")
            if dados.get("owner_otrs"):
                detalhe += " • Owner informado: " + dados["owner_otrs"]
            if dados.get("status_bloqueio"):
                detalhe += " • Status: " + dados["status_bloqueio"]
            row.detalhe = tk.Label(conteudo,text=detalhe,bg=self.c["painel"],fg=self.c["secundario"],
                                   font=(FONTE_PADRAO,8),anchor="w")
            row.detalhe.pack(fill="x",pady=(1,0))
        return row

    def atualizar_linha(self, row, numero, login, dados, propria):
        cor = self.cor if propria else self.c["secundario"]
        if row.link_ticket.cget("fg") != cor:
            row.link_ticket.configure(fg=cor)
        if row.nome_login.cget("text") != login or row.nome_login.cget("fg") != cor:
            row.nome_login.configure(text=login, fg=cor)
        bloqueado = bool(dados.get("bloqueio_confirmado"))
        if row.bloqueado != bloqueado:
            row.cadeado.destroy()
            row.cadeado = self.cadeado(row.texto, bloqueado)
            row.bloqueado = bloqueado
        if row.detalhe is not None:
            detalhe = dados["status"].replace("_", " ").capitalize()
            if dados.get("atribuido_em"):
                detalhe += " • " + dados["atribuido_em"].strftime("%d/%m %H:%M")
            if dados.get("owner_otrs"):
                detalhe += " • Owner informado: " + dados["owner_otrs"]
            if dados.get("status_bloqueio"):
                detalhe += " • Status: " + dados["status_bloqueio"]
            if row.detalhe.cget("text") != detalhe:
                row.detalhe.configure(text=detalhe)

    def cadeado(self, parent, bloqueado):
        cor = self.c["verde"] if bloqueado else self.cor
        from src.fila_me.ui.icones import carregar_icone

        imagem = carregar_icone(
            "lock",
            12,
            cor,
            self.root,
        )
        icone = tk.Label(
            parent,
            image=imagem,
            bg=self.c["painel"],
        )
        icone.pack(side="right", padx=(4, 2))
        icone.image = imagem
        return icone

    def cancelar_aviso_copia(self):
        if getattr(self, "copia_timer", None) is not None:
            self.root.after_cancel(self.copia_timer)
        self.copia_timer = None

    def copiar_ticket(self, numero):
        self.cancelar_aviso_copia()
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(str(numero))
            mensagem = "Número copiado"
        except tk.TclError:
            mensagem = "Não foi possível copiar"
        self.conexao.configure(text=mensagem)
        self.copia_timer = self.root.after(1500, self.limpar_aviso_copia)

    def limpar_aviso_copia(self):
        self.copia_timer = None
        if self.ativo:
            self.conexao.configure(text=self.estado_conexao)

    def fechar_menu_ticket(self):
        if getattr(self, "menu_contexto", None) is not None:
            self.menu_contexto.destroy()
        self.menu_contexto = None

    def menu_ticket(self, evento, numero, destino):
        self.fechar_menu_ticket()
        menu = tk.Menu(self.root, tearoff=False, bg=self.c["painel"], fg=self.c["texto"],
                       activebackground=self.c["botao"], activeforeground=self.c["texto"])
        self.menu_contexto = menu
        menu.add_command(label="Copiar número", command=lambda: self.copiar_ticket(numero))
        if destino:
            menu.add_command(label="Abrir no OTRS", command=lambda: webbrowser.open(destino))
        try:
            menu.tk_popup(evento.x_root, evento.y_root)
        finally:
            menu.grab_release()

    def encerrar(self):
        if not self.ativo:
            return
        self.ativo = False
        self.cancelar_aviso_copia()
        self.fechar_menu_ticket()
        if self.timer is not None:
            self.root.after_cancel(self.timer)
            self.timer = None
        if self.heartbeat_timer is not None:
            self.root.after_cancel(self.heartbeat_timer)
            self.heartbeat_timer = None
        self.root.attributes("-topmost", False)
        self.encerrar_menus()
        if self.popup_online and self.popup_online.winfo_exists():
            self.popup_online.destroy()
        if self.usuario["cargo"] == "tecnico":
            atualizar_status_trabalhando(self.usuario["id"], False)
        self.frame.destroy()

    def enviar_heartbeat(self):
        if not self.ativo or self.usuario["cargo"] != "tecnico":
            return
        try:
            atualizar_heartbeat(self.usuario["id"])
        except Exception as erro:
            print(f"Erro ao enviar heartbeat: {erro}")
        self.heartbeat_timer = self.root.after(5000, self.enviar_heartbeat)
