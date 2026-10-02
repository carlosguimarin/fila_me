from src.fila_me.config.settings import TECNICOS


class Fila:
    def __init__(self):
        self.indice_atual = 0

    @property
    def tecnico_atual(self):
        return TECNICOS[self.indice_atual]

    def proximo(self):
        self.indice_atual = (
            self.indice_atual + 1
        ) % len(TECNICOS)

    def anterior(self):
        self.indice_atual = (
            self.indice_atual - 1
        ) % len(TECNICOS)