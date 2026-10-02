function enviarTickets() {
    const widget = document.querySelector(
        "#Dashboard0120-TicketNew"
    );

    if (!widget) {
        return;
    }

    const tickets = [...widget.querySelectorAll(
        'a[href*="Action=AgentTicketZoom"]'
    )].map(link => link.textContent.trim());

    chrome.runtime.sendMessage({
        tipo: "tickets_otrs",
        tickets: tickets
    });
}

enviarTickets();

setInterval(enviarTickets, 5000);