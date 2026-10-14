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

## 4. Proprietário e bloqueio

O código ignora as células auxiliares `Flags`, encontra a célula cujo valor é exatamente `bloqueado` ou `desbloqueado` e lê o Owner da célula imediatamente anterior. Assim, os campos permanecem separados:

- `PROPRIETÁRIO` é enviado como Owner real;
- `BLOQUEAR` é enviado separadamente como `status` (`bloqueado` ou `desbloqueado`).

O estado recebido fica em `tickets.status_bloqueio`; não deve ser gravado em `owner_otrs`. O primeiro valor `bloqueado` também marca `tickets.bloqueio_confirmado = TRUE` e registra `bloqueado_em`. A confirmação é permanente: `desbloqueado` atualiza o estado atual, mas não remove a confirmação histórica. Isso preserva o verde se o chamado voltar para a fila. O campo não identifica quem realizou o bloqueio.

As contas do OTRS precisam exibir as colunas `PROPRIETÁRIO` e `BLOQUEAR` nos widgets monitorados. Se o cabeçalho ou a coluna não estiver presente, a extensão deixa o campo correspondente vazio; não infere o valor de outra coluna.

## 5. Leitura

A função conhecida produz objetos:

```javascript
{
    numero: numero,
    owner: owner,
    status: status
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

Isso não cria tickets/atribuições duplicados. Porém, se um ticket existente ainda estiver `AGUARDANDO_TECNICO`, o recebimento repetido pode reavaliar a atribuição existente no servidor/banco.

## 7. Comunicação

O `background.js` envia os dados para o servidor Python local.

Endpoints conhecidos:
- `/tickets`
- `/owner`

Os dois fluxos podem registrar a primeira observação de bloqueio: `/tickets` para Chamados Novos e `/owner` para Chamados Abertos. O servidor só marca tickets já registrados; ele não cria tickets ausentes do fluxo normal.

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
