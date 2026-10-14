"""Painéis ancorados, sem captura modal ou bindings globais permanentes."""
import tkinter as tk
import sys


def area_monitor(root, x, y):
    """Área útil do monitor da âncora, em coordenadas globais (inclusive negativas)."""
    if sys.platform == 'win32':
        import ctypes
        from ctypes import wintypes

        class MonitorInfo(ctypes.Structure):
            _fields_ = [('cbSize', wintypes.DWORD), ('rcMonitor', wintypes.RECT),
                        ('rcWork', wintypes.RECT), ('dwFlags', wintypes.DWORD)]

        user32 = ctypes.WinDLL('user32', use_last_error=True)
        user32.MonitorFromPoint.argtypes = [wintypes.POINT, wintypes.DWORD]
        user32.MonitorFromPoint.restype = wintypes.HANDLE
        user32.GetMonitorInfoW.argtypes = [wintypes.HANDLE, ctypes.POINTER(MonitorInfo)]
        user32.GetMonitorInfoW.restype = wintypes.BOOL
        monitor = user32.MonitorFromPoint(wintypes.POINT(x, y), 2)
        info = MonitorInfo()
        info.cbSize = ctypes.sizeof(info)
        if monitor and user32.GetMonitorInfoW(monitor, ctypes.byref(info)):
            r = info.rcWork
            return r.left, r.top, r.right, r.bottom
    # Tk fornece o desktop virtual nas demais plataformas.
    left, top = root.winfo_vrootx(), root.winfo_vrooty()
    return left, top, left + root.winfo_vrootwidth(), top + root.winfo_vrootheight()


def posicao_painel(x_ancora, y_ancora, largura_ancora, altura_ancora, w, h, area):
    left, top, right, bottom = area
    x = max(left, min(x_ancora + largura_ancora - w, right - w))
    y = y_ancora + altura_ancora + 4
    if y + h > bottom:
        y = y_ancora - h - 4
    y = max(top, min(y, bottom - h))
    return x, y


class MenuSuspenso:
    def __init__(self, root, ancora, construir, antes_abrir, fundo, borda):
        self.root, self.ancora, self.construir = root, ancora, construir
        self.antes_abrir, self.fundo, self.borda = antes_abrir, fundo, borda
        self.popup = None
        self.timer = None
        self.encerrado = False
        self.bindings = []
        ancora.bind('<Enter>', self.agendar_abertura, add='+')
        ancora.bind('<Leave>', self.agendar_fechamento, add='+')
        for evento, callback in (('<Button-1>', self.clique_fora), ('<Escape>', self.escape)):
            self.bindings.append((evento, root.bind(evento, callback, add='+')))

    def cancelar_timer(self):
        if self.timer is not None:
            self.root.after_cancel(self.timer)
            self.timer = None

    def agendar_abertura(self, evento=None):
        self.cancelar_timer()
        if not self.encerrado:
            self.timer = self.root.after(180, self.abrir)

    def agendar_fechamento(self, evento=None):
        self.cancelar_timer()
        if not self.encerrado:
            self.timer = self.root.after(250, self.fechar_se_fora)

    def contem(self, widget, x, y):
        return bool(widget and widget.winfo_exists() and
                    widget.winfo_rootx() <= x < widget.winfo_rootx() + widget.winfo_width() and
                    widget.winfo_rooty() <= y < widget.winfo_rooty() + widget.winfo_height())

    def dentro(self, x, y):
        return self.contem(self.ancora, x, y) or self.contem(self.popup, x, y)

    def fechar_se_fora(self):
        self.timer = None
        if not self.dentro(*self.root.winfo_pointerxy()):
            self.fechar()

    def clique_fora(self, evento):
        if not self.dentro(evento.x_root, evento.y_root):
            self.fechar()

    def escape(self, evento=None):
        self.fechar()

    def alternar(self):
        if self.popup and self.popup.winfo_exists():
            # Hover pode ter aberto antes do clique: clique confirma e dá foco.
            self.cancelar_timer()
            self.sincronizar_topo()
            self.popup.lift()
            self.popup.focus_set()
        else:
            self.abrir()
            if self.popup:
                self.popup.focus_set()

    def sincronizar_topo(self):
        if self.popup and self.popup.winfo_exists():
            self.popup.attributes('-topmost', self.root.attributes('-topmost'))
            self.popup.lift()

    def abrir(self):
        self.cancelar_timer()
        if self.encerrado or (self.popup and self.popup.winfo_exists()):
            return
        self.antes_abrir(self)
        self.popup = tk.Toplevel(self.root)
        self.popup.withdraw()
        self.popup.overrideredirect(True)
        self.popup.transient(self.root)
        self.popup.configure(bg=self.fundo, highlightbackground=self.borda, highlightthickness=1)
        self.popup.bind('<Enter>', lambda e: self.cancelar_timer(), add='+')
        self.popup.bind('<Leave>', self.agendar_fechamento, add='+')
        self.popup.bind('<Escape>', self.escape, add='+')
        self.construir(self.popup)
        self.popup.update_idletasks()
        w, h = self.popup.winfo_reqwidth(), self.popup.winfo_reqheight()
        ax, ay = self.ancora.winfo_rootx(), self.ancora.winfo_rooty()
        aw, ah = self.ancora.winfo_width(), self.ancora.winfo_height()
        area = area_monitor(self.root, ax + aw // 2, ay + ah // 2)
        x, y = posicao_painel(ax, ay, aw, ah, w, h, area)
        self.popup.geometry(f'+{x}+{y}')
        self.popup.attributes('-topmost', self.root.attributes('-topmost'))
        self.popup.deiconify()
        self.sincronizar_topo()

    def fechar(self):
        self.cancelar_timer()
        if self.popup and self.popup.winfo_exists():
            self.popup.destroy()
        self.popup = None

    def encerrar(self):
        self.fechar()
        self.encerrado = True
        for evento, identificador in self.bindings:
            self.root.unbind(evento, identificador)
        self.bindings.clear()
