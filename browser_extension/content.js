function encontrarOwnerDaLinha(linha) {

    const celulas = [
        ...linha.querySelectorAll("td")
    ];

    if (celulas.length === 0) {
        return null;
    }

    const ultimaCelula =
        celulas[celulas.length - 1];

    const elementoOwner =
        ultimaCelula.querySelector(
            "[title]"
        );

    if (!elementoOwner) {
        return null;
    }

    const owner =
        elementoOwner
            .getAttribute("title")
            ?.trim();

    return owner || null;
}


function encontrarTicketsPagina() {

    const links = [
        ...document.querySelectorAll(
            'a[href*="Action=AgentTicketZoom"]'
        )
    ];

    const tickets = [];

    const numerosProcessados =
        new Set();

    for (const link of links) {

        const numero =
            link.textContent.trim();

        if (!numero) {
            continue;
        }

        if (
            numerosProcessados.has(numero)
        ) {
            continue;
        }

        numerosProcessados.add(numero);

        const linha =
            link.closest("tr");

        if (!linha) {
            continue;
        }

        const owner =
            encontrarOwnerDaLinha(
                linha
            );

        tickets.push({
            numero: numero,
            owner: owner
        });
    }

    return tickets;
}


function enviarTickets() {

    const tickets =
        encontrarTicketsPagina();

    console.log(
        "Fila ME - tickets encontrados:",
        tickets
    );

    chrome.runtime.sendMessage({
        tipo:
            "tickets_otrs",

        tickets:
            tickets
    });
}


function executarLeitura() {

    enviarTickets();
}


executarLeitura();

setInterval(
    executarLeitura,
    5000
);