import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from src.fila_me.database.banco import (
    criar_tabelas,
    registrar_ticket_e_atribuir,
    buscar_ultimas_atribuicoes,
    buscar_proximo_tecnico,
)


HOST = "127.0.0.1"
PORTA = 8765


class ServidorFilaME(BaseHTTPRequestHandler):

    def enviar_json(self, dados, status=200):
        resposta = json.dumps(
            dados,
            ensure_ascii=False,
        ).encode("utf-8")

        self.send_response(status)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8",
        )
        self.send_header(
            "Content-Length",
            str(len(resposta)),
        )
        self.end_headers()

        self.wfile.write(resposta)

    def do_GET(self):
        if self.path != "/estado":
            self.send_error(404)
            return

        try:
            atribuicoes = buscar_ultimas_atribuicoes(9)
            proximo_tecnico = buscar_proximo_tecnico()

            historico = []

            for numero_ticket, tecnico, atribuido_em in atribuicoes:
                historico.append({
                    "numero_ticket": numero_ticket,
                    "tecnico": tecnico,
                    "atribuido_em": (
                        atribuido_em.isoformat()
                        if atribuido_em
                        else None
                    ),
                })

            self.enviar_json({
                "sucesso": True,
                "proximo_tecnico": proximo_tecnico,
                "historico": historico,
            })

        except Exception as erro:
            print(f"Erro ao consultar estado: {erro}")

            self.enviar_json(
                {
                    "sucesso": False,
                    "erro": str(erro),
                },
                500,
            )

    def do_POST(self):
        if self.path != "/tickets":
            self.send_error(404)
            return

        tamanho = int(
            self.headers.get("Content-Length", 0)
        )

        dados = self.rfile.read(tamanho)

        try:
            payload = json.loads(
                dados.decode("utf-8")
            )

            tickets = payload.get("tickets", [])

            novos = []
            existentes = []

            for numero_ticket in tickets:
                resultado = registrar_ticket_e_atribuir(
                    int(numero_ticket)
                )

                if resultado:
                    novos.append(resultado)
                else:
                    existentes.append(numero_ticket)

            print(
                f"Tickets recebidos: {tickets}"
            )

            print(
                f"Tickets novos: {novos}"
            )

            print(
                f"Tickets já conhecidos: {existentes}"
            )

            self.enviar_json({
                "sucesso": True,
                "novos": novos,
                "existentes": existentes,
            })

        except Exception as erro:
            print(
                f"Erro ao processar tickets: {erro}"
            )

            self.enviar_json(
                {
                    "sucesso": False,
                    "erro": str(erro),
                },
                400,
            )

    def log_message(self, formato, *args):
        pass


def iniciar_servidor():
    criar_tabelas()

    servidor = ThreadingHTTPServer(
        (HOST, PORTA),
        ServidorFilaME,
    )

    print(
        f"Fila ME aguardando tickets em "
        f"http://{HOST}:{PORTA}"
    )

    servidor.serve_forever()


if __name__ == "__main__":
    iniciar_servidor()