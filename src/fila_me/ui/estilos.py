FONTE_PADRAO = "Segoe UI"
TEMAS = {
    "escuro": {"fundo": "#202124", "painel": "#292B2E", "botao": "#34373B",
               "texto": "#F2F3F5", "secundario": "#AFB5BF", "borda": "#454951",
               "azul": "#5B9EFF", "verde": "#78D6A0", "campo": "#303339", "coral": "#FF8170", "saida": "#3D2828"},
    "claro": {"fundo": "#F4F6FA", "painel": "#FFFFFF", "botao": "#E4E8EF",
              "texto": "#212733", "secundario": "#576174", "borda": "#CCD3DF",
              "azul": "#245CC5", "verde": "#247348", "campo": "#FFFFFF", "coral": "#B84036", "saida": "#FBE5E1"},
}
# Compatibilidade com módulos antigos.
COR_FUNDO = TEMAS["escuro"]["fundo"]
COR_PAINEL = TEMAS["escuro"]["painel"]
COR_TEXTO = TEMAS["escuro"]["texto"]
COR_SECUNDARIO = TEMAS["escuro"]["secundario"]
COR_DESTAQUE = TEMAS["escuro"]["azul"]
COR_DESTAQUE_HOVER = "#76AEFF"
COR_BOTAO = TEMAS["escuro"]["botao"]


def cor_destaque(cor, tema):
    # Versões de maior contraste para as mesmas escolhas no tema claro.
    claras = {"#FF626B": "#BE303E", "#5B9EFF": "#245CC5", "#BA93FF": "#7145BF",
              "#EE80B8": "#AE306E", "#F0A45D": "#975317", "#F26F9A": "#B43664",
              "#FF8A76": "#A94232", "#E3AF52": "#865B12", "#71B7F6": "#276AA5",
              "#8F9CFF": "#4C57B7", "#D499F2": "#8647A6", "#EA74DB": "#A33495"}
    return claras.get(cor, cor) if tema == "claro" else cor


def cor_texto_botao(cor):
    """Escolhe texto claro/escuro pelo contraste, para todas as opções da paleta."""
    canais = [int(cor[i:i+2],16)/255 for i in (1,3,5)]
    linear = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in canais]
    luminancia = sum(v*p for v,p in zip(linear,(.2126,.7152,.0722)))
    return "#171A20" if luminancia > .179 else "#FFFFFF"


def nome_curto(nome):
    partes = str(nome or "").split()
    return " ".join((partes[0], partes[-1])) if len(partes) > 1 else " ".join(partes)
