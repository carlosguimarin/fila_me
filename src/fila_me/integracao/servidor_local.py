import json
from http.server import (
    BaseHTTPRequestHandler,
    ThreadingHTTPServer,
)

from src.fila_me.database.banco import (
    criar_tabelas,
    registrar_ticket_e_atribuir,
    buscar_ultimas_atribuicoes,
    buscar_proximo_tecnico,
    atualizar_atribuicao_owner,
)


HOST = "127.0.0.1"
PORTA = 8765


class ServidorFilaME(
    BaseHTTPRequestHandler
):

    def enviar_json(
        self,
        dados,
        status=200,
    ):

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

        self.wfile.write(
            resposta
        )

    def ler_json(self):

        tamanho = int(
            self.headers.get(
                "Content-Length",
                0,
            )
        )

        dados = self.rfile.read(
            tamanho
        )

        return json.loads(
            dados.decode("utf-8")
        )

    def do_GET(self):

        if self.path != "/estado":
            self.send_error(404)
            return

        try:

            atribuicoes = (
                buscar_ultimas_atribuicoes(9)
            )

            proximo_tecnico = (
                buscar_proximo_tecnico()
            )

            historico = []

            for (
                numero_ticket,
                tecnico,
                atribuido_em,
            ) in atribuicoes:

                historico.append({
                    "numero_ticket":
                        numero_ticket,

                    "tecnico":
                        tecnico,

                    "atribuido_em": (
                        atribuido_em.isoformat()
                        if atribuido_em
                        else None
                    ),
                })

            self.enviar_json({
                "sucesso": True,

                "proximo_tecnico":
                    proximo_tecnico,

                "historico":
                    historico,
            })

        except Exception as erro:

            print(
                f"Erro ao consultar estado: {erro}"
            )

            self.enviar_json(
                {
                    "sucesso": False,
                    "erro": str(erro),
                },
                500,
            )

    def do_POST(self):

        if self.path == "/tickets":

            self.processar_tickets()

            return

        if self.path == "/owner":

            self.processar_owner()

            return

        self.send_error(404)

    def processar_tickets(self):

        try:

            payload = self.ler_json()

            tickets = payload.get(
                "tickets",
                [],
            )

            novos = []
            existentes = []
            owners_processados = []

            for ticket in tickets:

                if isinstance(
                    ticket,
                    dict,
                ):

                    numero_ticket = (
                        ticket.get(
                            "numero"
                        )
                    )

                    owner = (
                        ticket.get(
                            "owner"
                        )
                    )

                else:

                    numero_ticket = ticket
                    owner = None

                if not numero_ticket:
                    continue

                numero_ticket = int(
                    numero_ticket
                )

                resultado = (
                    registrar_ticket_e_atribuir(
                        numero_ticket
                    )
                )

                if resultado:

                    resultado["owner"] = owner

                    novos.append(
                        resultado
                    )

                    print(
                        f"Ticket novo: "
                        f"{numero_ticket} "
                        f"| Owner: {owner}"
                    )

                else:

                    existentes.append({
                        "numero":
                            numero_ticket,

                        "owner":
                            owner,
                    })

                if owner:

                    resultado_owner = (
                        atualizar_atribuicao_owner(
                            numero_ticket,
                            owner,
                        )
                    )

                    if resultado_owner:

                        owners_processados.append(
                            resultado_owner
                        )

                        print(
                            f"Owner processado: "
                            f"Ticket "
                            f"{numero_ticket} "
                            f"| Owner: {owner} "
                            f"| Status: "
                            f"{resultado_owner['status']} "
                            f"| Tipo: "
                            f"{resultado_owner['tipo_atribuicao']}"
                        )

            print(
                f"Tickets recebidos: "
                f"{tickets}"
            )

            print(
                f"Tickets novos: "
                f"{novos}"
            )

            print(
                f"Tickets já conhecidos: "
                f"{existentes}"
            )

            print(
                f"Owners processados: "
                f"{owners_processados}"
            )

            self.enviar_json({
                "sucesso": True,

                "novos":
                    novos,

                "existentes":
                    existentes,

                "owners_processados":
                    owners_processados,
            })

        except Exception as erro:

            print(
                "Erro ao processar tickets: "
                f"{erro}"
            )

            self.enviar_json(
                {
                    "sucesso": False,
                    "erro": str(erro),
                },
                400,
            )

    def processar_owner(self):

        try:

            payload = self.ler_json()

            ticket_id = payload.get(
                "ticket_id"
            )

            owner = payload.get(
                "owner"
            )

            if not ticket_id:

                raise ValueError(
                    "TicketID não informado."
                )

            ticket_id = int(
                ticket_id
            )

            resultado = (
                atualizar_atribuicao_owner(
                    ticket_id,
                    owner,
                )
            )

            print(
                f"Owner recebido: "
                f"Ticket {ticket_id} "
                f"| Owner: {owner}"
            )

            self.enviar_json({
                "sucesso": True,

                "ticket_id":
                    ticket_id,

                "owner":
                    owner,

                "atribuicao":
                    resultado,
            })

        except Exception as erro:

            print(
                "Erro ao processar Owner: "
                f"{erro}"
            )

            self.enviar_json(
                {
                    "sucesso": False,
                    "erro": str(erro),
                },
                400,
            )

    def log_message(
        self,
        formato,
        *args,
    ):
        pass


def iniciar_servidor():

    criar_tabelas()

    servidor = ThreadingHTTPServer(
        (
            HOST,
            PORTA,
        ),
        ServidorFilaME,
    )

    print(
        "Fila ME aguardando tickets em "
        f"http://{HOST}:{PORTA}"
    )

    servidor.serve_forever()


if __name__ == "__main__":

    iniciar_servidor()