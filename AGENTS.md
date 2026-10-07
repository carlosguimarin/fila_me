# AGENTS.md

# FILA ME — Contexto e Instruções do Projeto

> **Finalidade deste arquivo:** este documento consolida as decisões, regras de negócio, arquitetura, implementação, testes, problemas e pendências definidos durante o desenvolvimento do FILA ME nesta conversa. Ele deve ser tratado como contexto permanente pelo Codex.
>
> **Regra principal:** o código existente e as regras de negócio documentadas aqui não devem ser simplificados, removidos ou reinterpretados sem confirmação do responsável pelo projeto.

---

## 0. CLASSIFICAÇÃO DO ESTADO

Para evitar confusão entre ideias e implementação real, este documento usa:

- **IMPLEMENTADO** — existe ou existiu no código do projeto conforme o histórico.
- **TESTADO** — foi executado/testado e há resultado conhecido.
- **PENDENTE** — ainda precisa ser feito.
- **DISCUTIDO MAS NÃO IMPLEMENTADO** — foi planejado ou avaliado, mas não deve ser tratado como funcionalidade existente.
- **DECISÃO DEFINITIVA** — regra/decisão que não deve ser revertida sem discussão.
- **QUESTÃO EM ABERTO** — comportamento que ainda precisa ser investigado/decidido.

Quando houver diferença entre uma versão anterior e o arquivo atual enviado pelo usuário, o arquivo atual deve ser considerado a fonte de verdade do código, e a evolução histórica é descrita separadamente.

---

# 1. OBJETIVO DO PROJETO

## 1.1 O que é o FILA

O **Fila ME** é uma aplicação desktop desenvolvida em Python para controlar a distribuição/ordem de atendimento de chamados entre técnicos de TI.

O projeto foi criado para auxiliar o trabalho da equipe de suporte que utiliza o **OTRS**. O FILA mantém uma fila centralizada para que os computadores dos técnicos compartilhem a mesma ordem de atendimento.

A aplicação mostra:

- quem é o próximo técnico;
- histórico das últimas atribuições;
- os técnicos atualmente considerados trabalhando;
- informações relacionadas aos chamados acompanhados pelo OTRS.

## 1.2 Problema que resolve

O objetivo é evitar que a distribuição de chamados dependa apenas de controle manual entre os técnicos.

O sistema precisa:

1. identificar um chamado novo no OTRS;
2. verificar se o chamado já foi registrado anteriormente;
3. se for novo, atribuí-lo provisoriamente ao próximo técnico da fila;
4. avançar a fila de forma centralizada;
5. depois conferir quem realmente aparece como Owner no OTRS;
6. tratar corretamente situações em que o Owner é o técnico esperado, outro técnico ou Supervisão;
7. manter o histórico para auditoria;
8. permitir que vários computadores utilizem a mesma fila.

## 1.3 Relação com o OTRS

O FILA **não possui atualmente uma integração oficial/API do OTRS**.

A abordagem atual é:

- o técnico mantém o OTRS aberto no navegador;
- uma extensão de navegador lê a página do dashboard;
- a extensão identifica tickets e Owner;
- a extensão envia os dados para um pequeno servidor HTTP local;
- o servidor local chama as funções do banco PostgreSQL central.

O OTRS continua sendo a fonte do Owner real do chamado.

A atribuição feita pelo FILA é inicialmente uma **atribuição provisória de fila**, e não deve ser confundida com o Owner efetivamente definido no OTRS.

---

# 2. ARQUITETURA ATUAL

## 2.1 Visão geral

A arquitetura atual é:

```text
OTRS no navegador
        │
        ▼
Extensão Fila ME - OTRS
        │
        │ HTTP localhost
        ▼
Servidor Python local :8765
        │
        ▼
Funções de banco Python
        │
        ▼
Neon PostgreSQL central
        ▲
        │
Aplicações FILA dos técnicos
        │
        ▼
Interface Tkinter
```

Cada computador executa sua própria instância do FILA e sua própria extensão/browser, mas todos os computadores consultam o mesmo banco PostgreSQL no Neon.

## 2.2 Tecnologias

- Python
- Tkinter para interface desktop
- PostgreSQL hospedado no Neon
- `psycopg` para conexão PostgreSQL
- `python-dotenv` para carregar `DATABASE_URL`
- PyInstaller para gerar o `.exe`
- JavaScript para a extensão do navegador
- Manifest V3 para a extensão
- HTTP local usando `http.server`
- Git/GitHub para versionamento
- VS Code como ambiente de desenvolvimento

## 2.3 Estrutura conhecida do projeto

A estrutura principal utilizada é:

```text
fila_me/
├── .env
├── .gitignore
├── FilaME.spec
├── dist/
│   ├── FilaME.exe
│   ├── .env
│   └── FilaME.zip
├── src/
│   └── fila_me/
│       ├── app.py
│       ├── database/
│       │   └── banco.py
│       ├── integracao/
│       │   └── servidor_local.py
│       └── ui/
│           ├── tela_login.py
│           └── janela_principal.py
└── extensão do OTRS
    ├── manifest.json
    ├── content.js
    └── background.js
```

A extensão do OTRS é tratada como parte do projeto, embora os arquivos dela possam estar em uma pasta de extensão separada da estrutura Python.

Não inventar outros arquivos como existentes sem verificar o repositório.

---

# 3. ARQUIVOS E RESPONSABILIDADES

## 3.1 `src\fila_me\app.py`

**IMPLEMENTADO**

Ponto de entrada da aplicação Python.

É utilizado para iniciar o FILA durante o desenvolvimento, por exemplo:

```powershell
python -m src.fila_me.app
```

O fluxo de aplicação envolve login, abertura da janela principal e encerramento.

---

## 3.2 `src\fila_me\database\banco.py`

**IMPLEMENTADO / EM ALTERAÇÃO**

É o módulo central de acesso ao PostgreSQL e contém as regras de persistência da fila.

Entre as responsabilidades já implementadas:

- conexão com PostgreSQL;
- criação/verificação das tabelas;
- registro de tickets;
- identificação de ticket novo/repetido;
- escolha do próximo técnico;
- atualização do estado da fila;
- busca do histórico;
- criação e busca de usuários;
- atualização de status `trabalhando`;
- processamento do Owner do OTRS;
- tratamento de Supervisão;
- tratamento de outro técnico assumindo chamado.

### Estado importante atual

O arquivo `banco.py` enviado mais recentemente pelo usuário é a versão-base atual. Nessa versão, a tabela `usuarios` contém `trabalhando`, mas **não contém ainda `ultimo_heartbeat` no `CREATE TABLE`**, e as consultas atuais de técnicos trabalhando ainda usam apenas:

```sql
trabalhando = TRUE
```

Portanto, o heartbeat foi decidido e o banco Neon já recebeu alterações SQL, mas a integração completa do heartbeat no código ainda está em andamento.

O SQL já executado no Neon foi:

```sql
ALTER TABLE usuarios
ADD COLUMN IF NOT EXISTS ultimo_heartbeat TIMESTAMP;
```

e:

```sql
UPDATE usuarios
SET ultimo_heartbeat = NULL;
```

Esses comandos foram executados com sucesso/sem necessidade de retorno visual.

---

## 3.3 `src\fila_me\integracao\servidor_local.py`

**IMPLEMENTADO**

Servidor HTTP local em:

```text
127.0.0.1:8765
```

Endpoints atuais:

```text
POST /tickets
POST /owner
GET  /estado
```

Responsabilidades:

- receber tickets da extensão;
- chamar `registrar_ticket_e_atribuir`;
- receber Owner;
- chamar `atualizar_atribuicao_owner`;
- fornecer estado para a interface.

O heartbeat **não deve ser colocado no servidor local sem necessidade**. A decisão atual é que o heartbeat seja atualizado diretamente pelo aplicativo Python através do módulo de banco.

---

## 3.4 `src\fila_me\ui\tela_login.py`

**IMPLEMENTADO**

Tela de login.

Foi ajustada para permitir:

- Enter no campo de e-mail → foco no campo de senha;
- Enter no campo de senha → realizar login.

---

## 3.5 `src\fila_me\ui\janela_principal.py`

**IMPLEMENTADO, COM ALTERAÇÃO DE HEARTBEAT EM TRANSIÇÃO**

Interface principal atual conhecida:

- nome do usuário;
- cargo;
- título `Fila ME`;
- botão de janela sempre no topo;
- botão `Sair`;
- indicador `Próximo`;
- lista de últimas atribuições.

Dimensão atual:

```text
365x410
```

A interface usa Tkinter.

### Sempre no topo

O botão com ícone de alfinete alterna:

```python
root.attributes("-topmost", True/False)
```

Quando ativado, o botão muda visualmente.

### Histórico

A interface mostra as últimas 9 atribuições.

Exemplo visual:

```text
#12345 → Carlos
#12346 → Luís
#12347 → Daniel
```

Quando o técnico visualizando a tela é o técnico da atribuição, o texto recebe destaque.

### Atualização

O estado é atualizado periodicamente, atualmente a cada 5 segundos.

### Heartbeat

Foi preparada uma versão da `janela_principal.py` que:

- importa `atualizar_heartbeat`;
- envia heartbeat a cada 5 segundos;
- inicia heartbeat ao abrir a janela do técnico;
- cancela o callback ao sair;
- limpa o status ao encerrar normalmente.

**IMPORTANTE:** a versão heartbeat-enabled foi fornecida durante a conversa, mas não houve confirmação final de que ela foi salva no repositório. O Codex deve verificar o arquivo real antes de assumir que essa versão está instalada.

---

# 4. REGRAS DE NEGÓCIO

Esta seção é crítica. **Não alterar sem confirmação.**

## 4.1 Técnicos que participam da fila

Somente usuários que atendem aos critérios abaixo participam da seleção normal:

```text
cargo = 'tecnico'
ativo = TRUE
trabalhando = TRUE
```

Com o heartbeat concluído, a intenção definitiva é considerar também a validade temporal do heartbeat.

O objetivo do heartbeat é evitar que um técnico permaneça artificialmente como trabalhando depois de:

- queda de energia;
- travamento;
- encerramento forçado;
- crash do processo;
- fechamento que não execute o código de logout.

---

## 4.2 Ordem da fila

A fila é centralizada no PostgreSQL.

O estado da fila é mantido em:

```text
fila_estado
```

com o campo:

```text
ultimo_tecnico_id
```

O banco é responsável por determinar o próximo técnico.

Não usar estado local em cada computador para determinar a vez.

### Ordem normal

Exemplo:

```text
Carlos → Luís → Daniel → Carlos → Luís → Daniel...
```

A ordem é calculada a partir dos técnicos elegíveis e do último técnico registrado.

---

## 4.3 Ticket novo

Um ticket é considerado novo quando seu número ainda não existe na tabela `tickets`.

O identificador único é:

```text
numero_ticket
```

A tabela possui:

```sql
numero_ticket BIGINT PRIMARY KEY
```

O registro usa:

```sql
ON CONFLICT (numero_ticket) DO NOTHING
```

Portanto:

- se o ticket nunca apareceu → novo;
- se já apareceu anteriormente → não é novo;
- se o mesmo ticket aparecer novamente semanas ou meses depois → continua sendo o mesmo ticket conhecido.

Não criar uma nova atribuição simplesmente porque o ticket voltou a aparecer no dashboard.

---

## 4.4 Atribuição inicial/provisória

Quando um ticket novo é detectado:

1. o sistema registra o ticket;
2. verifica técnicos elegíveis;
3. escolhe o próximo técnico;
4. cria uma atribuição provisória;
5. avança a fila imediatamente.

**DECISÃO DEFINITIVA: a atribuição inicial já consome a vez.**

Não esperar o Owner real do OTRS para avançar a fila.

Exemplo:

```text
Próximo = Carlos
Ticket novo → atribuído provisoriamente a Carlos
Fila passa a apontar para Luís
```

---

## 4.5 Atribuição provisória ≠ Owner real

O campo:

```text
atribuicoes.tecnico
```

representa o técnico escolhido pelo FILA na atribuição.

O campo:

```text
atribuicoes.owner_otrs
```

representa o Owner observado no OTRS.

Esses campos não devem ser tratados como equivalentes.

O Owner real é conferido posteriormente pela extensão do navegador.

---

## 4.6 Owner igual ao técnico originalmente atribuído

Se o Owner real no OTRS for o mesmo técnico originalmente atribuído:

```text
Owner OTRS == tecnico da atribuição
```

então:

- a atribuição é confirmada;
- o Owner é registrado;
- o status passa para `CONFIRMADO`;
- a fila **não muda novamente**.

A vez já havia sido consumida pela atribuição inicial.

---

## 4.7 Outro técnico assume o chamado

Se outro técnico assume um ticket que foi provisoriamente atribuído a alguém:

### Regra definitiva

A situação depende do estado do técnico originalmente atribuído.

#### Caso A — técnico originalmente atribuído continua trabalhando

Se o técnico original ainda estiver trabalhando/online:

- o outro técnico é registrado como Owner real;
- a atribuição pode ser confirmada com o Owner real;
- **o outro técnico não consome a vez da fila se ele estiver fora da vez**;
- a fila permanece como estava.

Exemplo:

```text
Fila:
Carlos → Luís → Daniel

Ticket foi provisoriamente para Luís.
Luís continua trabalhando.
Daniel assume o ticket.

Daniel está fora da vez.
A fila NÃO avança por causa de Daniel.
```

#### Caso B — técnico originalmente atribuído saiu

Se o técnico originalmente atribuído já não estiver trabalhando:

- outro técnico pode assumir o ticket;
- se esse outro técnico for exatamente o próximo técnico naquele momento, ele pode consumir a vez.

Exemplo:

```text
Luís recebeu provisoriamente.
Luís fecha o FILA.
Luís fica offline.
Daniel é o próximo.
Daniel assume o ticket.
Daniel pode consumir a vez.
```

Não inventar uma mudança de fila simplesmente porque o técnico original saiu. A reavaliação ocorre quando outro técnico realmente assume o chamado.

---

## 4.8 Supervisão / Supervisão como coringa

**DECISÃO DEFINITIVA**

Supervisão é tratada como:

```text
Coringa / Wildcard
```

Supervisão **não consome a vez do técnico**.

Se um ticket foi provisoriamente atribuído a um técnico e Supervisão assume:

```text
fila antes:
Carlos → Luís → Daniel

ticket atribuído provisoriamente a Carlos

Supervisão assume

resultado:
Carlos continua sendo o próximo
```

Para isso existe:

```text
ultimo_tecnico_id_anterior
```

na atribuição.

Quando a atribuição ainda está:

```text
status = 'PENDENTE'
tipo_atribuicao = 'TECNICO'
```

e Supervisão assume, o estado anterior da fila deve ser restaurado.

---

## 4.9 Owner desconhecido / não cadastrado

Exemplo:

```text
Admin OTRS
```

Se o Owner não corresponder a um usuário cadastrado:

- registrar `owner_otrs`;
- não inventar usuário;
- não alterar a fila;
- não alterar a atribuição para um técnico inexistente.

A informação deve permanecer para auditoria.

---

## 4.10 Sem técnico trabalhando

Se não houver técnico elegível:

```text
status = 'AGUARDANDO_TECNICO'
```

e:

```text
tecnico = NULL
```

O sistema não deve inventar uma atribuição.

---

## 4.11 Ticket já conhecido

Se `numero_ticket` já existir em `tickets`:

- não criar novo ticket;
- não consumir nova vez;
- não criar nova atribuição inicial.

Ainda é possível processar Owner posteriormente, conforme o fluxo da extensão.

---

# 5. DECISÕES IMPORTANTES JÁ TOMADAS

## DECISÃO DEFINITIVA — Banco central

Todos os computadores usam o mesmo PostgreSQL no Neon.

Não usar banco SQLite local como fonte oficial da fila.

## DECISÃO DEFINITIVA — Estado centralizado

A vez da fila fica no PostgreSQL.

Isso evita que:

```text
PC do Carlos
PC do Luís
PC do Daniel
```

tenham filas independentes.

## DECISÃO DEFINITIVA — Ticket como chave única

O número do ticket é a identidade do chamado.

## DECISÃO DEFINITIVA — Atribuição inicial consome a vez

Não esperar Owner.

## DECISÃO DEFINITIVA — Supervisão é coringa

Supervisão não consome a vez.

## DECISÃO DEFINITIVA — Owner real é informação separada

Atribuição provisória e Owner OTRS são conceitos diferentes.

## DECISÃO DEFINITIVA — Heartbeat

A presença do técnico deve ser baseada em heartbeat para evitar `trabalhando = TRUE` permanente após falhas.

Meta atual:

```text
heartbeat a cada ~5 segundos
considerar válido por ~15 segundos
```

## DECISÃO DEFINITIVA — OTRS via navegador

Não existe integração API implementada atualmente. A extensão lê o DOM do dashboard.

## DECISÃO DEFINITIVA — Não criar nova Release GitHub

A versão oficial `v1.0.0` já foi criada anteriormente.

Para alterações posteriores, a intenção é:

- atualizar código;
- gerar novo `.exe`;
- entregar o `.exe` aos usuários;
- fazer Git/PR/merge normalmente;
- **não criar nova Release GitHub**, salvo decisão futura.

---

# 6. O QUE JÁ FOI IMPLEMENTADO

## Banco

**IMPLEMENTADO**

- conexão com Neon PostgreSQL;
- criação das tabelas;
- tickets únicos;
- fila centralizada;
- usuários;
- atribuições;
- histórico;
- Owner OTRS;
- tratamento de Supervisão;
- tratamento de Owner desconhecido;
- seleção do próximo técnico;
- controle `trabalhando`.

## Interface

**IMPLEMENTADO**

- login;
- Enter entre campos;
- janela principal;
- nome/cargo;
- próximo técnico;
- histórico;
- botão Sair;
- sempre no topo;
- destaque visual das próprias atribuições.

## Servidor local

**IMPLEMENTADO**

```text
127.0.0.1:8765
```

com `/tickets`, `/owner` e `/estado`.

## Extensão

**IMPLEMENTADO**

- leitura de `Chamados Novos`;
- leitura de `Chamados Abertos`;
- extração de número do ticket;
- tentativa de extração do Owner;
- envio para Python via `127.0.0.1:8765`.

## Build

**IMPLEMENTADO**

PyInstaller é utilizado.

Comando utilizado:

```powershell
Remove-Item -Recurse -Force .\build
Remove-Item -Recurse -Force .\dist
pyinstaller .\FilaME.spec
```

Depois:

```powershell
Copy-Item .\.env .\dist\.env
```

E ZIP:

```powershell
Compress-Archive -Path .\dist\FilaME.exe, .\dist\.env -DestinationPath .\dist\FilaME.zip -Force
```

O executável é:

```text
dist\FilaME.exe
```

---

# 7. O QUE JÁ FOI TESTADO

## 7.1 Banco

**TESTADO**

Foi demonstrado que a lógica de registro/consulta do banco funcionou.

Durante testes de fila, tickets foram registrados e a ordem foi conferida pela interface.

## 7.2 Ordem da fila

**TESTADO**

Foi realizado teste manual com tickets atribuídos a:

- Luís;
- Carlos;
- Daniel.

A ordem observada foi ajustada e conferida manualmente.

Também houve teste envolvendo três tickets para Luís e um ticket para Carlos, seguido de ajuste manual de `fila_estado` para validar a próxima posição.

## 7.3 Registro de tickets

**TESTADO**

Foi observado que tickets foram registrados no banco e apareceram no histórico.

## 7.4 Extensão OTRS

**TESTADO**

A extensão conseguiu:

- localizar widgets;
- localizar links de tickets;
- enviar tickets para o Python;
- enviar Owner.

## 7.5 Build

**TESTADO**

O build com PyInstaller funcionou.

Houve inicialmente:

```text
PermissionError: [WinError 5] Access is denied
```

porque o `FilaME.exe` antigo estava aberto.

Depois de fechar o executável, o build funcionou.

## 7.6 Distribuição

**TESTADO**

Foi gerado:

```text
FilaME.exe
FilaME.zip
```

O `.env` precisou ser copiado para `dist` porque o executável procura o arquivo no próprio diretório quando está congelado pelo PyInstaller.

---

# 8. PROBLEMAS / BUGS CONHECIDOS

## 8.1 Owner do OTRS pode ser identificado incorretamente

**BUG CONHECIDO / PENDENTE**

Houve um caso concreto:

```text
Ticket 4102
Owner real no OTRS: Luís
owner_otrs registrado no banco: "bloqueado"
```

A suspeita é a implementação atual:

```javascript
const elementoOwner = ultimaCelula.querySelector("[title]");
```

pode estar encontrando um elemento de status/bloqueio na última célula, e não necessariamente o elemento que representa o Owner.

Isso ainda precisa ser investigado.

**IMPORTANTE:** não substituir a lógica atual por outra sem primeiro analisar o DOM real do OTRS.

---

## 8.2 Heartbeat ainda não está completamente integrado

**PENDENTE**

O banco Neon já recebeu:

```sql
ultimo_heartbeat
```

mas o arquivo `banco.py` atualmente enviado pelo usuário ainda não contém a implementação final.

A versão heartbeat-enabled de `janela_principal.py` foi criada durante a conversa, mas não houve confirmação final de que ela está salva no projeto.

---

## 8.3 Possível inconsistência em versões anteriores do heartbeat

Durante uma versão intermediária gerada anteriormente, a função `atualizar_status_trabalhando()` chegou a ter três placeholders SQL, mas apenas dois parâmetros na tupla.

Isso deve ser considerado um alerta histórico: **não reutilizar cegamente versões anteriores do `banco.py`**.

A fonte correta é sempre o arquivo atual do repositório/arquivo fornecido pelo usuário.

---

# 9. FUNCIONALIDADES PENDENTES

## PENDENTE — Finalizar heartbeat

Implementar corretamente:

```text
usuarios.ultimo_heartbeat
```

e utilizar a validade temporal para determinar técnicos online.

Comportamento desejado:

```text
heartbeat a cada 5 segundos
validade: 15 segundos
```

Ao sair normalmente:

```text
trabalhando = FALSE
ultimo_heartbeat = NULL
```

Após crash/queda:

```text
não recebe heartbeat
↓
15 segundos
↓
deixa de ser elegível
```

## PENDENTE — Testar heartbeat

Testes mínimos desejados:

1. abrir aplicação;
2. login do técnico;
3. consultar `ultimo_heartbeat`;
4. verificar atualização aproximadamente a cada 5 segundos;
5. fechar normalmente;
6. verificar `trabalhando = FALSE` e heartbeat limpo;
7. opcionalmente encerrar o processo à força e esperar mais de 15 segundos para verificar que deixa de ser considerado online.

Não criar uma bateria excessiva de testes se um teste direto for suficiente.

## PENDENTE — Corrigir leitura do Owner

Investigar DOM do OTRS para garantir que o Owner verdadeiro seja lido.

## PENDENTE — Gerar novo executável após heartbeat

Depois de validar o código:

```powershell
Remove-Item -Recurse -Force .\build
Remove-Item -Recurse -Force .\dist
pyinstaller .\FilaME.spec
Copy-Item .\.env .\dist\.env
Compress-Archive -Path .\dist\FilaME.exe, .\dist\.env -DestinationPath .\dist\FilaME.zip -Force
```

Não criar nova Release GitHub.

---

# 10. BANCO DE DADOS

## 10.1 Banco escolhido

**DECISÃO DEFINITIVA**

PostgreSQL hospedado no **Neon**.

A aplicação usa `psycopg`.

A variável de conexão é:

```text
DATABASE_URL
```

armazenada em:

```text
.env
```

O `.env` não deve ser commitado no Git.

## 10.2 SQLite

SQLite foi inicialmente discutido/testado para a funcionalidade de tickets.

Foi criada uma estrutura de banco local durante desenvolvimento, incluindo algo como:

```text
src/fila_me/database
```

e teste de:

```text
Já viu? False
Já viu depois de registrar? True
```

Posteriormente, o banco local foi removido e a decisão foi migrar a fonte oficial para PostgreSQL central.

**DECISÃO DEFINITIVA:** não voltar para SQLite como banco oficial da fila.

## 10.3 Tabela `tickets`

Campos principais:

```text
numero_ticket BIGINT PRIMARY KEY
criado_em TIMESTAMP
```

Finalidade:

- registrar todos os tickets conhecidos;
- garantir unicidade;
- impedir que o mesmo ticket consuma a fila novamente.

## 10.4 Tabela `fila_estado`

Campos:

```text
id
indice_atual
ultimo_tecnico_id
```

O campo principal atualmente usado para a lógica da fila é:

```text
ultimo_tecnico_id
```

Existe controle com:

```sql
FOR UPDATE
```

durante a atribuição para evitar decisões concorrentes inconsistentes.

## 10.5 Tabela `atribuicoes`

Campos principais:

```text
id
numero_ticket
tecnico
atribuido_em
status
owner_otrs
confirmado_em
tipo_atribuicao
ultimo_tecnico_id_anterior
```

Finalidade:

- registrar a atribuição inicial;
- registrar o técnico provisório;
- registrar Owner real;
- controlar estado da atribuição;
- diferenciar atribuição `TECNICO` e `SUPERVISAO`;
- guardar o estado anterior da fila para o comportamento coringa da Supervisão.

## 10.6 Tabela `usuarios`

Campos conhecidos:

```text
id
nome
email
senha_hash
cargo
ativo
trabalhando
criado_em
ultimo_heartbeat
```

`cargo` aceita:

```text
tecnico
supervisao
```

`ativo` indica se o usuário está ativo.

`trabalhando` representa o estado de trabalho atual.

`ultimo_heartbeat` foi adicionado no banco Neon para implementar presença confiável.

## 10.7 Heartbeat no banco

SQL já executado:

```sql
ALTER TABLE usuarios
ADD COLUMN IF NOT EXISTS ultimo_heartbeat TIMESTAMP;
```

e:

```sql
UPDATE usuarios
SET ultimo_heartbeat = NULL;
```

A regra planejada é considerar online somente quando:

```sql
ultimo_heartbeat >= CURRENT_TIMESTAMP - INTERVAL '15 seconds'
```

---

# 11. GIT

## 11.1 Repositório

GitHub:

```text
https://github.com/carlosguimarin/fila_me
```

## 11.2 Branches

Branches relevantes:

```text
main
carlos
luis
feature/banco-tickets
```

O desenvolvimento principal do Carlos ocorre em:

```text
carlos
```

## 11.3 Proteção da `main`

A `main` está protegida.

Regras já configuradas:

- PR obrigatório;
- 1 aprovação;
- resolução das conversas;
- Code Owners não configurado;
- force push bloqueado;
- exclusão da branch bloqueada;
- squash permitido.

## 11.4 Fluxo

Não fazer desenvolvimento diretamente em `main`.

Fluxo esperado:

```text
branch de trabalho
↓
commit
↓
push
↓
Pull Request
↓
aprovação
↓
merge
```

## 11.5 Histórico importante

Foi criada a branch:

```text
feature/banco-tickets
```

para trabalhar na persistência de tickets.

Também houve uso de:

```powershell
git push origin carlos:main --force
```

e:

```powershell
git fetch
git reset --hard origin/main
```

Isso foi parte do histórico de sincronização, mas **não deve ser repetido sem necessidade**, principalmente por causa da proteção atual da `main`.

## 11.6 Cuidado

O Codex deve:

- verificar branch atual;
- verificar `git status`;
- não sobrescrever trabalho de outra branch;
- não usar `reset --hard` destrutivo sem confirmação;
- não usar `push --force` sem necessidade e autorização explícita;
- não substituir código funcional apenas para "simplificar".

---

# 12. INTERAÇÃO COM O OTRS

## 12.1 URL

Dashboard utilizado:

```text
https://helpdesk.mpsc.mp.br/otrs/index.pl?Action=AgentDashboard
```

## 12.2 Abordagem atual

A extensão lê diretamente o DOM da página do dashboard.

Não existe API oficial integrada atualmente.

## 12.3 Widgets

A extensão procura:

```text
Chamados Novos
Chamados Abertos
```

através do título do widget.

## 12.4 Tickets

Os links são encontrados por:

```javascript
a[href*="Action=AgentTicketZoom"]
```

O número do ticket vem do texto do link.

A extensão evita processar o mesmo número duas vezes dentro da mesma leitura usando `Set`.

## 12.5 Polling

A leitura é feita aproximadamente a cada:

```text
5 segundos
```

## 12.6 Comunicação

A extensão usa:

```text
127.0.0.1:8765
```

Endpoint:

```text
POST /tickets
```

para tickets.

E:

```text
POST /owner
```

para Owner.

---

# 13. EXTENSÃO DO OTRS

## 13.1 `content.js`

Responsabilidades:

- encontrar widgets;
- localizar tickets;
- extrair Owner;
- enviar mensagens para `background.js`.

A implementação atual usa uma função semelhante a:

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

Essa implementação é justamente a parte suspeita no bug do Owner.

## 13.2 `background.js`

Recebe mensagens:

```text
tickets_otrs
owner_otrs
```

e faz `fetch` para o servidor Python local.

## 13.3 `manifest.json`

Manifest V3.

Permissões incluem:

```text
storage
```

e host permissions para:

```text
https://helpdesk.mpsc.mp.br/otrs/*
http://127.0.0.1:8765/*
```

---

# 14. INTERFACE

## 14.1 Login

A tela de login possui:

- e-mail;
- senha;
- navegação por Enter.

## 14.2 Janela principal

A janela mostra:

```text
[Nome]
[Técnico/Supervisão]

             Fila ME

Próximo: Carlos

Últimas atribuições

#ticket → técnico
#ticket → técnico
...
```

## 14.3 Sempre no topo

O usuário pode ativar/desativar a janela sempre no topo.

## 14.4 Sair

Ao clicar em `Sair`:

- encerra a janela;
- deve marcar o técnico como não trabalhando;
- com heartbeat concluído, também deve limpar/cancelar o heartbeat.

---

# 15. BUILD E DISTRIBUIÇÃO

## 15.1 PyInstaller

Arquivo de especificação:

```text
FilaME.spec
```

Build:

```powershell
Remove-Item -Recurse -Force .\build
Remove-Item -Recurse -Force .\dist
pyinstaller .\FilaME.spec
```

## 15.2 `.env`

O executável precisa do:

```text
dist\.env
```

porque o código identifica o diretório do executável quando está congelado.

Copiar:

```powershell
Copy-Item .\.env .\dist\.env
```

## 15.3 ZIP

```powershell
Compress-Archive -Path .\dist\FilaME.exe, .\dist\.env -DestinationPath .\dist\FilaME.zip -Force
```

## 15.4 Segurança

O `.env` contém a `DATABASE_URL`.

Portanto:

- não commitar `.env`;
- não expor a credencial publicamente;
- ter cuidado ao compartilhar ZIP;
- a distribuição atual foi aceita pelo responsável do projeto, mas isso continua sendo um ponto de segurança relevante.

---

# 16. COMPORTAMENTOS QUE NÃO DEVEM SER ALTERADOS SEM CONFIRMAÇÃO

O Codex não deve alterar silenciosamente:

1. a regra de que atribuição inicial consome a vez;
2. o tratamento de Supervisão como coringa;
3. a separação entre `tecnico` provisório e `owner_otrs`;
4. a regra de ticket único;
5. a centralização da fila no Neon;
6. o uso de `FOR UPDATE` na determinação da fila;
7. a regra de outro técnico fora da vez;
8. a regra do técnico original ainda trabalhando;
9. a regra de técnico original offline;
10. a regra de Owner desconhecido;
11. a interface existente;
12. o fluxo de extensão → servidor → banco;
13. a estrutura de Git protegida;
14. a decisão de não criar uma nova Release para cada atualização;
15. funcionalidades existentes sem antes entender sua finalidade.

---

# 17. REGRAS PARA O CODEX

## 17.1 Antes de alterar

Sempre:

1. verificar o código existente;
2. verificar branch;
3. verificar `git status`;
4. localizar a função/arquivo responsável;
5. entender a regra de negócio relacionada;
6. evitar criar uma solução paralela quando já existe uma implementação.

## 17.2 Não simplificar regras

Uma implementação aparentemente mais simples não deve substituir uma regra de negócio complexa.

Exemplo:

> "Se outro técnico assumiu, basta mudar `ultimo_tecnico_id`."

Isso está errado sem analisar a regra completa.

É necessário considerar:

- quem recebeu a atribuição original;
- se ele continua trabalhando;
- quem é o Owner real;
- quem é o próximo;
- se é Supervisão;
- se o ticket ainda está PENDENTE;
- se a vez já foi consumida.

## 17.3 Não remover funcionalidades

Não remover:

- histórico;
- Owner;
- Supervisão;
- `ultimo_tecnico_id_anterior`;
- servidor local;
- extensão;
- sempre no topo;
- login;
- controle de técnicos trabalhando.

Sem confirmação explícita.

## 17.4 Conflitos

Se o código existente contradizer uma regra documentada:

**não escolher silenciosamente uma das versões.**

Informar:

```text
CONFLITO DETECTADO:
regra documentada: ...
código atual: ...
impacto: ...
```

e pedir confirmação quando necessário.

## 17.5 Grandes alterações

Antes de grandes mudanças:

- explicar o impacto;
- informar arquivos afetados;
- explicar se o banco muda;
- explicar se a extensão muda;
- explicar se o `.exe` precisará ser reconstruído.

## 17.6 Alterações de banco

Alterações de schema devem ser compatíveis com banco existente.

Preferir:

```sql
ADD COLUMN IF NOT EXISTS
```

quando apropriado.

Não apagar dados/tabelas sem confirmação.

## 17.7 Heartbeat

O heartbeat é uma melhoria de presença, não uma nova regra de fila.

**Não usar o heartbeat como justificativa para mudar a lógica de atribuição/Owner já definida.**

## 17.8 Código

O responsável pelo projeto prefere:

- instruções diretas;
- alterações completas de arquivo quando solicitado;
- caminho exato do arquivo;
- evitar snippets ambíguos;
- evitar problemas de indentação;
- desenvolvimento em VS Code;
- terminal principalmente para Git/comandos.

---

# 18. HISTÓRICO DE DECISÕES / EVOLUÇÃO

## Fase inicial — SQLite

Foi considerado SQLite para registrar tickets vistos.

Foi demonstrado:

```text
Já viu? False
Já viu depois de registrar? True
```

Depois surgiu a necessidade de vários computadores compartilharem o mesmo estado.

## Migração para PostgreSQL

Foi decidido utilizar PostgreSQL centralizado.

O Neon passou a ser o banco oficial.

## Fila central

A fila passou a usar:

```text
fila_estado.ultimo_tecnico_id
```

com lock transacional.

## Integração OTRS

Como não havia API integrada, foi escolhida leitura da página via extensão.

## Owner

Foi adicionada a distinção entre:

```text
atribuição inicial
Owner real
```

## Supervisão

Foi definido que Supervisão é coringa e não consome a vez.

Foi criado:

```text
ultimo_tecnico_id_anterior
```

para restaurar a posição anterior.

## Outro técnico

A regra foi refinada para considerar se o técnico original ainda está trabalhando.

## Heartbeat

Foi identificado que apenas:

```text
trabalhando = TRUE
```

não é suficiente porque crash/queda de energia pode deixar estado stale.

Foi decidido adicionar:

```text
ultimo_heartbeat
```

com janela de aproximadamente 15 segundos.

---

# 19. QUESTÕES EM ABERTO

1. Finalizar a integração do heartbeat no `banco.py`.
2. Confirmar que a `janela_principal.py` atual usa o heartbeat.
3. Corrigir/validar a extração do Owner no OTRS.
4. Fazer teste mínimo do heartbeat.
5. Gerar novo `.exe` após validação.
6. Fazer commit/PR/merge das alterações pendentes.

Não assumir que questões acima já foram resolvidas apenas porque uma solução foi discutida ou um arquivo foi gerado durante a conversa.

---

# 20. ESTADO ATUAL

## Funcionando

- aplicação desktop Python;
- login;
- interface principal;
- consulta do próximo técnico;
- histórico;
- fila central no Neon;
- registro único de tickets;
- atribuição inicial;
- regras de Supervisão;
- regras de Owner;
- servidor local;
- extensão do OTRS;
- build PyInstaller;
- distribuição do `.exe`.

## Não está totalmente resolvido

- leitura confiável do Owner em todos os casos;
- heartbeat ainda em integração/validação.

## Em desenvolvimento agora

**Heartbeat de presença dos técnicos.**

O banco Neon já possui a coluna:

```text
ultimo_heartbeat
```

mas o código atual enviado pelo usuário ainda precisa receber a implementação final.

## Próximo passo recomendado

1. Atualizar `src\fila_me\database\banco.py` com heartbeat, preservando toda a lógica existente.
2. Atualizar/confirmar `src\fila_me\ui\janela_principal.py`.
3. Executar o app.
4. Verificar `ultimo_heartbeat` no Neon.
5. Testar logout normal.
6. Se necessário, fazer um teste de encerramento forçado.
7. Gerar novo `.exe`.
8. Commitar em branch de trabalho.
9. Push.
10. PR para `main`.

---

# 21. CONTEXTO PARA O CODEX — RESUMO

1. FILA ME é uma aplicação Python desktop para controlar a fila de atendimento de chamados do OTRS.
2. O OTRS continua sendo a fonte do Owner real; o FILA faz uma atribuição inicial/provisória.
3. A fila é centralizada no Neon PostgreSQL e compartilhada entre os computadores.
4. Ticket é identificado exclusivamente por `numero_ticket`; ticket já visto nunca consome a fila novamente.
5. A atribuição inicial de um ticket novo consome a vez imediatamente.
6. Owner igual ao técnico originalmente atribuído apenas confirma a atribuição; não avança a fila novamente.
7. Outro técnico assumir não significa automaticamente que a fila deve avançar.
8. Se o técnico original ainda estiver trabalhando, outro técnico fora da vez não altera a fila.
9. Se o técnico original estiver offline, outro técnico pode consumir a vez somente se for o próximo naquele momento.
10. Supervisão é coringa e não consome a vez.
11. Para Supervisão existe `ultimo_tecnico_id_anterior`, usado para restaurar a fila quando a atribuição ainda é PENDENTE/TECNICO.
12. Owner desconhecido é apenas registrado em `owner_otrs`; não altera a fila.
13. Sem técnico trabalhando, novo ticket fica `AGUARDANDO_TECNICO`.
14. Estado da fila usa `fila_estado.ultimo_tecnico_id` e lock `FOR UPDATE`.
15. Banco oficial é PostgreSQL/Neon; SQLite foi descartado como fonte oficial.
16. A extensão OTRS lê o DOM do dashboard e envia tickets/Owner para `127.0.0.1:8765`.
17. Servidor Python local possui `/tickets`, `/owner` e `/estado`.
18. Existe bug conhecido na leitura do Owner: um caso registrou `bloqueado` em vez do Owner real Luís.
19. Heartbeat é a melhoria em desenvolvimento: aproximadamente 5s de intervalo e 15s de validade.
20. Neon já recebeu a coluna `usuarios.ultimo_heartbeat`.
21. O `banco.py` atualmente fornecido pelo usuário ainda não possui a implementação final do heartbeat.
22. A versão heartbeat da `janela_principal.py` foi criada, mas precisa ser confirmada no código real.
23. Não alterar a lógica de fila/Owner durante a implementação do heartbeat.
24. Não criar soluções paralelas antes de analisar o código existente.
25. Não remover funcionalidades ou regras sem confirmação.
26. Branch principal de desenvolvimento do Carlos é `carlos`; `main` é protegida por PR.
27. Não usar force push/reset destrutivo sem autorização.
28. PyInstaller gera `dist/FilaME.exe`; o `.env` precisa acompanhar o executável.
29. A versão oficial `v1.0.0` já existe; não criar nova Release para cada atualização.
30. Próximo passo: finalizar/testar heartbeat, depois corrigir Owner e gerar novo executável.
