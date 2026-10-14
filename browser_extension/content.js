function lerCelula(celula) {
    if (!celula) {
        return null;
    }

    const elementoComTitulo = celula.querySelector("[title]");
    const valor = elementoComTitulo
        ? elementoComTitulo.getAttribute("title")
        : celula.innerText;

    return valor?.trim() || null;
}


function encontrarDadosDaLinha(linha) {
    // Owner e BLOQUEAR são células distintas. O status tem o texto exato
    // bloqueado/desbloqueado e o Owner fica imediatamente antes dele.
    // Ignore as células auxiliares Flags do OTRS.
    const celulasDados = [...linha.cells].filter(
        celula => !celula.classList.contains("Flags")
    );
    let indiceStatus = -1;
    for (let indice = celulasDados.length - 1; indice >= 0; indice--) {
        const valor = lerCelula(celulasDados[indice])
            ?.toLocaleLowerCase("pt-BR");
        if (["bloqueado", "desbloqueado"].includes(valor)) {
            indiceStatus = indice;
            break;
        }
    }

    if (indiceStatus < 1) {
        return { owner: null, status: null };
    }

    const status = lerCelula(celulasDados[indiceStatus])
        .toLocaleLowerCase("pt-BR");
    const owner = lerCelula(celulasDados[indiceStatus - 1]);
    const ownerNormalizado = owner?.toLocaleLowerCase("pt-BR");
    const ownerValido = ["bloqueado", "desbloqueado"].includes(ownerNormalizado)
        ? null
        : owner;

    return { owner: ownerValido, status };
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

        const { owner, status } =
            encontrarDadosDaLinha(linha);

        tickets.push({
            numero: numero,
            owner: owner,
            status: status
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

        if (!ticket.owner && !ticket.status) {
            continue;
        }

        console.log(
            "Fila ME - Chamado Aberto para conferência:",
            ticket
        );

        chrome.runtime.sendMessage({
            tipo: "owner_otrs",
            ticket_id: ticket.numero,
            owner: ticket.owner,
            status: ticket.status
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
