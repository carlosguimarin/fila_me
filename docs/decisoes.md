# Fila ME — Decisões de Projeto

## D001 — Banco central

**Decisão:** usar Neon PostgreSQL como estado compartilhado.

**Motivo:** várias máquinas precisam enxergar exatamente a mesma fila.

---

## D002 — Ticket como identidade

**Decisão:** número do ticket é a identidade global.

**Motivo:** o mesmo ticket pode aparecer repetidamente no dashboard.

---

## D003 — Atribuição inicial avança a fila

**Decisão:** o primeiro técnico escolhido para um novo ticket consome a vez.

**Motivo:** a fila representa a distribuição automática do sistema, não quem posteriormente assumiu manualmente o ticket.

---

## D004 — Owner não corrige fila

**Decisão:** Owner posterior do OTRS não altera a fila.

**Motivo:** um técnico pode assumir um ticket fora da vez por necessidade interna.

---

## D005 — Supervisor não participa

**Decisão:** supervisores não entram na rotação.

**Motivo:** supervisão é função distinta da distribuição automática de tickets aos técnicos.

---

## D006 — Supervisor no histórico

**Decisão:** quando o Owner é supervisor registrado, o histórico exibe `Supervisão`.

**Motivo:** evitar que a interface atribua falsamente a responsabilidade final ao técnico provisional.

---

## D007 — Owner desconhecido

**Decisão:** não inferir cargo.

**Exemplo:**
`Admin OTRS`

**Comportamento:** registrar Owner e não inferir cargo nem alterar a fila por causa da identidade desconhecida. Separadamente, se a atribuição estiver `AGUARDANDO_TECNICO`, a regra D016 pode atribuir o ticket a um técnico elegível.

---

## D008 — Técnicos em trabalho

**Decisão:** somente `tecnico + ativo + trabalhando` participa.

**Motivo:** um usuário cadastrado mas ausente não deve receber tickets.

---

## D009 — Polling

**Decisão:** a extensão consulta o dashboard em aproximadamente 5 segundos.

**Motivo:** V1 simples e sem dependência de API do OTRS.

---

## D010 — Extensão não decide regras

**Decisão:** extensão somente coleta dados.

**Motivo:** regra de negócio deve ficar centralizada e testável em Python/banco.

---

## D011 — UI Tkinter

**Decisão:** V1 usa Tkinter.

**Motivo:** aplicação desktop pequena, simples e rápida de distribuir.

---

## D012 — Executável PyInstaller

**Decisão:** distribuir como `.exe` quando necessário.

**Motivo:** usuário final não precisa configurar Python.

---

## D013 — `.env` fora do Git

**Decisão:** credenciais ficam em `.env`.

**Motivo:** impedir exposição da conexão Neon.

---

## D014 — `main` protegido

**Decisão:** mudanças entram em `main` por PR.

**Motivo:** permitir testes/revisão antes da integração final.

---

## D015 — Documentação como memória compartilhada

**Decisão:** decisões importantes devem existir no repositório, não apenas em conversas de ChatGPT.

**Motivo:** Carlos e Luís usam chats/ambientes de IA separados.

---

## D016 — Reavaliar atribuições aguardando técnico

**Decisão:** um ticket ativo já registrado como `AGUARDANDO_TECNICO` pode ser reavaliado quando for recebido novamente pela integração e houver técnico elegível.

**Ordem:** processar o Owner primeiro. Se for reconhecido como Supervisão, confirmar como `SUPERVISAO` sem atribuí-lo à fila técnica. Se ainda estiver aguardando e houver técnico elegível, atribuir o próximo da fila na atribuição existente.

**Proteções:** não criar ticket/atribuição duplicada; não varrer nem reintroduzir registros que não foram recebidos pela integração; usar o heartbeat e o bloqueio transacional da fila.

---

## D017 — Integração da V2 de interface

**Decisão:** a V2 pode reorganizar aparência e navegação, mas não pode mover as regras de fila para o cliente nem remover contratos do backend sem revisão e migração explícitas.

**Referência:** seguir o checklist em `integracao_v2.md`; ao concluir a integração, consolidar decisões permanentes nos documentos funcionais e remover o guia temporário se ele não tiver mais valor histórico.
