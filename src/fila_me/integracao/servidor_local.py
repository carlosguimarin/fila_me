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
    atribuir_ticket_aguardando,
    registrar_status_bloqueio,
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
                    status = ticket.get(
                        "status"
                    )

                else:

                    numero_ticket = ticket
                    owner = None
                    status = None

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

                estado_bloqueio = (
                    registrar_status_bloqueio(
                        numero_ticket,
                        status,
                    )
                )

                if resultado:

                    resultado["owner"] = owner
                    resultado["estado_bloqueio"] = (
                        estado_bloqueio
                    )

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

                        "estado_bloqueio":
                            estado_bloqueio,
                    })

                if owner:

                    resultado_owner = (
                        atualizar_atribuicao_owner(
                            numero_ticket,
                            owner,
                        )
                    )

                    if resultado_owner:

                        # Não propaga Owners desconhecidos recebidos do DOM.
                        # O banco devolve o nome cadastrado ou o sentinela.
                        owner = resultado_owner["owner"]
                        if resultado:
                            resultado["owner"] = owner
                        if (
                            existentes
                            and existentes[-1]["numero"] == numero_ticket
                        ):
                            existentes[-1]["owner"] = owner

                        owners_processados.append(
                            resultado_owner
                        )

                        print(
                            f"Owner processado: "
                            f"Ticket "
                            f"{numero_ticket} "
                            f"| Owner: {resultado_owner['owner']} "
                            f"| Status: "
                            f"{resultado_owner['status']} "
                            f"| Tipo: "
                            f"{resultado_owner['tipo_atribuicao']}"
                        )

                resultado_aguardando = (
                    atribuir_ticket_aguardando(
                        numero_ticket
                    )
                )

                if resultado_aguardando:
                    print(
                        f"Ticket aguardando atribuído: "
                        f"{numero_ticket} "
                        f"| Técnico: "
                        f"{resultado_aguardando['tecnico']}"
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

            status = payload.get(
                "status"
            )

            if not ticket_id:

                raise ValueError(
                    "TicketID não informado."
                )

            ticket_id = int(
                ticket_id
            )

            resultado = None
            if owner:
                resultado = (
                    atualizar_atribuicao_owner(
                        ticket_id,
                        owner,
                    )
                )

            estado_bloqueio = (
                registrar_status_bloqueio(
                    ticket_id,
                    status,
                )
            )

            resultado_aguardando = (
                atribuir_ticket_aguardando(
                    ticket_id
                )
            )

            if resultado:
                owner = resultado["owner"]

            print(
                f"Ticket recebido: "
                f"{ticket_id} "
                f"| Owner: {owner} "
                f"| Status: {status}"
            )

            self.enviar_json({
                "sucesso": True,

                "ticket_id":
                    ticket_id,

                "owner":
                    owner,

                "estado_bloqueio":
                    estado_bloqueio,

                "atribuicao":
                    resultado,

                "reatribuicao":
                    resultado_aguardando,
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
