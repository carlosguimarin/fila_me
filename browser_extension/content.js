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
        ultimaCelula.querySelector("[title]");

    if (!elementoOwner) {
        return null;
    }

    const owner =
        elementoOwner
            .getAttribute("title")
            ?.trim();

    return owner || null;
}


function encontrarWidgetPorTitulo(titulo) {

    const widgets = [
        ...document.querySelectorAll(
            ".WidgetSimple.CanDrag"
        )
    ];

    return widgets.find(widget => {

        const cabecalho =
            widget.querySelector(".Header");

        if (!cabecalho) {
            return false;
        }

        return (
            cabecalho.innerText.trim() === titulo
        );
    }) || null;
}


function encontrarTicketsNoWidget(widget) {

    if (!widget) {
        return [];
    }

    const links = [
        ...widget.querySelectorAll(
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
            encontrarOwnerDaLinha(linha);

        tickets.push({
            numero: numero,
            owner: owner
        });
    }

    return tickets;
}


function enviarTicketsNovos(tickets) {

    if (tickets.length === 0) {
        return;
    }

    console.log(
        "Fila ME - Chamados Novos:",
        tickets
    );

    chrome.runtime.sendMessage({
        tipo: "tickets_otrs",
        tickets: tickets
    });
}


function enviarOwnersChamadosAbertos(tickets) {

    for (const ticket of tickets) {

        if (!ticket.owner) {
            continue;
        }

        console.log(
            "Fila ME - Chamado Aberto para conferência:",
            ticket
        );

        chrome.runtime.sendMessage({
            tipo: "owner_otrs",
            ticket_id: ticket.numero,
            owner: ticket.owner
        });
    }
}


function executarLeitura() {

    const widgetChamadosNovos =
        encontrarWidgetPorTitulo(
            "Chamados Novos"
        );

    const widgetChamadosAbertos =
        encontrarWidgetPorTitulo(
            "Chamados Abertos"
        );


    const ticketsNovos =
        encontrarTicketsNoWidget(
            widgetChamadosNovos
        );

    const ticketsAbertos =
        encontrarTicketsNoWidget(
            widgetChamadosAbertos
        );


    console.log(
        "Fila ME - Chamados Novos encontrados:",
        ticketsNovos
    );

    console.log(
        "Fila ME - Chamados Abertos encontrados:",
        ticketsAbertos
    );


    enviarTicketsNovos(
        ticketsNovos
    );

    enviarOwnersChamadosAbertos(
        ticketsAbertos
    );
}


executarLeitura();

setInterval(
    executarLeitura,
    5000
);