# Fila ME — Integração OTRS e Extensão

## 1. Página monitorada

Dashboard do OTRS:

```text
https://helpdesk.mpsc.mp.br/otrs/index.pl?Action=AgentDashboard
```

A extensão lê a página geral do dashboard.

## 2. Estratégia

A V1 não utiliza API do OTRS.

Foi adotada leitura do DOM porque a integração por API ainda não estava disponível/implementada.

## 3. Ticket

A extensão procura links contendo:

```css
a[href*="Action=AgentTicketZoom"]
```

O texto do link é usado como número do ticket.

Um `Set` evita processar o mesmo número duas vezes dentro da mesma leitura da página.

## 4. Owner

O Owner é obtido da última célula (`td`) da linha do ticket.

A implementação validada usa o elemento que possui `[title]` e lê:

```javascript
getAttribute("title")
```

A função conhecida:

```javascript
function encontrarOwnerDaLinha(linha) {
    const celulas = [...linha.querySelectorAll("td")];
    if (celulas.length === 0) return null;

    const ultimaCelula = celulas[celulas.length - 1];
    const elementoOwner = ultimaCelula.querySelector("[title]");

    if (!elementoOwner) return null;

    const owner = elementoOwner.getAttribute("title")?.trim();
    return owner || null;
}
```

## 5. Leitura

A função conhecida produz objetos:

```javascript
{
    numero: numero,
    owner: owner
}
```

E envia:

```javascript
chrome.runtime.sendMessage({
    tipo: "tickets_otrs",
    tickets: tickets
});
```

## 6. Polling

A leitura é repetida aproximadamente a cada 5 segundos.

Isso é esperado e NÃO significa que cada leitura deva criar uma nova atribuição.

A proteção de duplicidade fica no banco.

## 7. Comunicação

O `background.js` envia os dados para o servidor Python local.

Endpoints conhecidos:
- `/tickets`
- `/owner`

Servidor:

```text
127.0.0.1:8765
```

## 8. Extensão

O manifesto possui permissões para:
- página do OTRS;
- localhost.

Para desenvolvimento:
- abrir `edge://extensions`;
- localizar `Fila ME - OTRS`;
- clicar em `Reload`.

Para depuração:
- F12;
- Console.

Log conhecido:

```text
Fila ME - tickets encontrados:
```

## 9. Problemas evitados

### Não usar AgentTicketZoom como fonte obrigatória

A V1 foi construída lendo a tabela do dashboard.

### Não confiar no Owner para determinar a fila

Owner é informação posterior do OTRS.

A fila já foi avançada na atribuição inicial.

### Não considerar `Admin OTRS` supervisor automaticamente

Somente usuários registrados no banco podem ser classificados com base no cargo.
