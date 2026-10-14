"""Contratos de leitura e presença da integração visual, sem Neon ou Tk real."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


RAIZ = Path(__file__).resolve().parents[1]


def carregar_modulo(nome, caminho, modulos):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    modulo = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, modulos):
        spec.loader.exec_module(modulo)
    return modulo


class CursorFalso:
    def __init__(self, linhas):
        self.linhas = linhas
        self.consulta = None
        self.parametros = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, consulta, parametros=None):
        self.consulta, self.parametros = consulta, parametros

    def fetchall(self):
        return self.linhas


class ConexaoFalsa:
    def __init__(self, cursor):
        self.cursor_falso = cursor

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def cursor(self):
        return self.cursor_falso


class TesteIntegracaoV2(unittest.TestCase):
    def test_painel_consulta_sem_escrever_na_fila(self):
        dotenv = types.ModuleType("dotenv")
        dotenv.load_dotenv = lambda *args: None
        banco = carregar_modulo(
            "banco_teste_v2",
            RAIZ / "src/fila_me/database/banco.py",
            {"psycopg": types.ModuleType("psycopg"), "dotenv": dotenv},
        )
        cursor = CursorFalso([
            (4102, "Luís", None, "CONFIRMADO", "Luís", "TECNICO", "bloqueado", True),
            (4103, "Carlos", None, "CONFIRMADO", "Mateus", "SUPERVISAO", None, False),
        ])
        banco.conectar = lambda: ConexaoFalsa(cursor)
        banco.buscar_tecnicos_trabalhando = lambda: [(1, "Carlos"), (2, "Luís")]
        banco.buscar_proximo_tecnico = lambda: "Carlos"

        painel = banco.buscar_painel_visual({"nome": "Luís"}, "meus")

        self.assertEqual(painel["proximo"], "Carlos")
        self.assertTrue(painel["historico"][0]["meu"])
        self.assertFalse(painel["historico"][1]["meu"])
        self.assertTrue(painel["historico"][0]["bloqueio_confirmado"])
        self.assertFalse(painel["historico"][1]["bloqueio_confirmado"])
        self.assertEqual(painel["historico"][0]["status_bloqueio"], "bloqueado")
        self.assertEqual(cursor.parametros, ("Luís",))
        self.assertIn("SELECT", cursor.consulta)
        self.assertNotIn("UPDATE", cursor.consulta)
        self.assertEqual(len(painel["online"]), 2)

    def test_encerrar_cancela_heartbeat_e_limpa_presenca(self):
        banco = types.ModuleType("src.fila_me.database.banco")
        eventos = []
        banco.atualizar_heartbeat = lambda usuario_id: eventos.append(("heartbeat", usuario_id))
        banco.atualizar_status_trabalhando = (
            lambda usuario_id, trabalhando: eventos.append(("presenca", usuario_id, trabalhando))
        )
        banco.buscar_painel_visual = lambda *args, **kwargs: None
        modulo = carregar_modulo(
            "janela_teste_v2",
            RAIZ / "src/fila_me/ui/janela_principal.py",
            {"src.fila_me.database.banco": banco},
        )
        janela = modulo.JanelaPrincipal.__new__(modulo.JanelaPrincipal)
        janela.ativo = True
        janela.usuario = {"id": 7, "cargo": "tecnico"}
        janela.atribuicao_do_usuario = lambda dados: False
        linha_supervisao = {
            "numero_ticket": 2026100554003418,
            "tecnico": "Luís Bolina Martins",
            "tipo_atribuicao": "SUPERVISAO",
            "owner_otrs": "Mateus Marinho Furtado",
        }
        self.assertEqual(
            janela.dados_apresentacao_historico(linha_supervisao)[0],
            "Supervisão",
        )
        janela.timer = "estado"
        janela.heartbeat_timer = "heartbeat"
        janela.popup_online = None
        janela.cancelar_aviso_copia = lambda: None
        janela.fechar_menu_ticket = lambda: None
        janela.encerrar_menus = lambda: None
        janela.frame = types.SimpleNamespace(destroy=lambda: eventos.append(("destroy",)))
        janela.root = types.SimpleNamespace(
            after_cancel=lambda identificador: eventos.append(("cancel", identificador)),
            attributes=lambda *args: eventos.append(("topo", *args)),
        )

        janela.encerrar()
        janela.enviar_heartbeat()

        self.assertIn(("cancel", "estado"), eventos)
        self.assertIn(("cancel", "heartbeat"), eventos)
        self.assertIn(("presenca", 7, False), eventos)
        self.assertNotIn(("heartbeat", 7), eventos)


if __name__ == "__main__":
    unittest.main()
