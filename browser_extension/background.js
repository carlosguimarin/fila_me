chrome.runtime.onMessage.addListener(
    (mensagem) => {

        if (
            mensagem.tipo ===
            "tickets_otrs"
        ) {

            fetch(
                "http://127.0.0.1:8765/tickets",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        tickets:
                            mensagem.tickets
                    })
                }
            )
                .then(
                    resposta =>
                        resposta.json()
                )
                .then(
                    resultado => {

                        console.log(
                            "Fila ME - resposta do Python:",
                            resultado
                        );
                    }
                )
                .catch(
                    erro => {

                        console.error(
                            "Fila ME - Python não está disponível:",
                            erro
                        );
                    }
                );

            return;
        }


        if (
            mensagem.tipo ===
            "owner_otrs"
        ) {

            fetch(
                "http://127.0.0.1:8765/owner",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        ticket_id:
                            mensagem.ticket_id,

                        owner:
                            mensagem.owner
                    })
                }
            )
                .then(
                    resposta =>
                        resposta.json()
                )
                .then(
                    resultado => {

                        console.log(
                            "Fila ME - resposta do Owner:",
                            resultado
                        );
                    }
                )
                .catch(
                    erro => {

                        console.error(
                            "Fila ME - Python não está disponível para Owner:",
                            erro
                        );
                    }
                );

            return;
        }
    }
);