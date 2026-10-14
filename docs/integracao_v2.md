# Integração da V2 de interface

## Objetivo e duração deste guia

Este guia orienta a integração da V2 de interface que Luís está desenvolvendo com as regras e o backend mantidos na branch de Carlos. A V2 pode reorganizar completamente as telas, mas a alteração visual não deve mudar silenciosamente a distribuição, o acesso ao Neon, a integração OTRS ou o estado de presença dos técnicos.

Use o guia durante a preparação e revisão da integração. Depois que ela terminar, incorpore as decisões permanentes aos documentos de regras, arquitetura, banco de dados e testes. Este checklist pode então ser removido ou movido para o histórico se não continuar útil.

## Estado do repositório observado

Em 2026-10-14, o checkout estava limpo na branch `carlos`, alinhado ao `origin/carlos`. A referência local `origin/luis` apontava para `0b5282d` (`Sincronizacao com a main`); a comparação local com `origin/carlos` mostrava somente mudanças em arquivos `__pycache__`. Isso **não prova** que Luís não tenha uma V2 em andamento no seu computador: a referência remota pode não conter trabalho local ainda não enviado.

Antes da integração real, Luís precisa publicar a versão que deseja integrar. Depois, atualize as referências com `git fetch origin` e compare os commits e arquivos atuais. Não use o snapshot acima como se fosse o conteúdo final da V2.

## Fontes de verdade e autoridade

1. A branch mais recente de Carlos fornece o comportamento atual do backend e da fila.
2. As decisões estáveis estão em `regras_negocio.md`, `decisoes.md` e `banco_dados.md`.
3. Este guia define como preservar esses contratos durante a integração visual.
4. Se o código contradisser as regras, pare a integração daquele comportamento e resolva a divergência com Carlos; não escolha silenciosamente um lado.

## Limite da mudança visual

Luís pode mudar layout, componentes, navegação, cores, dimensões, responsividade e a forma de apresentar o estado. A mudança de UI não deve:

- calcular localmente quem é o próximo técnico;
- decidir ou avançar `fila_estado`;
- acessar o PostgreSQL diretamente pela interface ou pelo navegador;
- duplicar regras de Owner/Supervisão dentro dos componentes visuais;
- retirar presença, logout, heartbeat, histórico, pinagem ou tratamento de erros sem acordo explícito;
- mudar formato de senha, schema, endpoints ou assinaturas compartilhadas sem mapear todos os consumidores e revisar migração.

Se a V2 usar uma arquitetura diferente de Tkinter, preserve as regras no módulo de banco/serviço do Python e forneça à interface uma camada de chamadas clara. Não copie a regra de fila para JavaScript ou para o estado local da tela.

## Contratos atuais que a V2 precisa preservar

### Banco e fila

- Neon PostgreSQL é a autoridade compartilhada; não substituir por estado local.
- `tickets.numero_ticket` identifica unicamente um chamado.
- `atribuicoes.tecnico` representa a atribuição do FILA; `owner_otrs` representa o Owner recebido do OTRS. São campos diferentes.
- Uma atribuição nova consome a vez ao ser criada. A seleção e o avanço usam `fila_estado.ultimo_tecnico_id` sob bloqueio transacional.
- Técnicos elegíveis precisam estar ativos, trabalhando e ter heartbeat nos últimos 15 segundos. A UI envia heartbeat aproximadamente a cada 5 segundos.
- Quando não há técnico elegível, um ticket novo fica `AGUARDANDO_TECNICO`.
- Quando um ticket ativo já conhecido em `AGUARDANDO_TECNICO` volta a ser recebido, o servidor processa Owner primeiro. Se não tiver sido confirmado como Supervisão e continuar aguardando, `atribuir_ticket_aguardando()` pode atribuir a atribuição existente ao próximo técnico elegível e avançar a fila. Não deve criar nova linha de ticket/atribuição nem varrer registros ausentes do OTRS.
- Supervisão é coringa: não participa da rotação. Owner reconhecido como supervisor deve resultar em `tipo_atribuicao = 'SUPERVISAO'`, histórico como `Supervisão` e sem consumo de vez.
- Owner igual ou diferente do técnico é tratado pela função de banco existente. A UI não deve reimplementar essas decisões.
- Owner desconhecido não permite inferir cargo. A identidade desconhecida não altera a fila por si só.

### Presença e ciclo de vida da tela

- Ao abrir a área do técnico, marcar presença e iniciar o heartbeat.
- Repetir heartbeat em torno de 5 segundos; validade no banco: 15 segundos.
- Ao sair normalmente, cancelar o callback e limpar `trabalhando`/heartbeat.
- No crash, a expiração do heartbeat deve retirar o técnico da elegibilidade sem depender de logout.
- Supervisão pode usar a aplicação, mas nunca aparece como técnico elegível.
- Fechar a tela ou retornar ao login deve preservar o ciclo de encerramento e não deixar callbacks ativos.

### Atualização e dados apresentados

- A tela atualiza próximo e histórico aproximadamente a cada 5 segundos.
- O histórico atual mostra até 9 atribuições recentes e distingue técnico, Supervisão e `Aguardando técnico`.
- A UI deve tratar indisponibilidade do banco/servidor sem travar o loop da interface e sem apresentar dados locais como autoridade da fila.
- O botão de janela sempre no topo é uma funcionalidade existente. Se a V2 mudar sua apresentação, preserve a ação ou combine explicitamente sua remoção.

### Integração OTRS e servidor local

- A extensão envia dados ao servidor Python em `127.0.0.1:8765`; o navegador não acessa o Neon.
- Endpoints atuais: `POST /tickets`, `POST /owner` e `GET /estado`.
- A extensão coleta; a decisão de atribuição pertence ao backend.
- Há um bug conhecido na extração do Owner: valores como `bloqueado`, `desbloqueado`, categorias ou assunto do chamado apareceram em `owner_otrs`. Não trate esse campo como identidade confiável quando contiver esses valores e não “corrija” a extração sem conferir o DOM real.

## Procedimento de integração

1. **Confirmar publicação:** obter de Luís o commit/branch que realmente contém a V2. Verificar que alterações locais foram commitadas e enviadas; não depender apenas do nome `luis`.
2. **Sincronizar referências:** executar `git fetch origin`; anotar os commits de `origin/carlos`, `origin/luis` e `origin/main` antes de integrar.
3. **Revisar o escopo:** comparar os nomes dos arquivos e o diff completo. Separar mudanças de UI das mudanças de backend, schema, extensão e build.
4. **Limpar artefatos:** não integrar `.env`, `dist/`, `build/`, `.venv/`, `__pycache__/` ou `.pyc`. Se bytecode rastreado aparecer no diff, confirmar/remover do conjunto de integração sem descartar código-fonte.
5. **Criar uma integração revisável:** usar uma branch temporária baseada na branch atualizada de Carlos para combinar a V2. Não sobrescrever `carlos` nem `main`; não usar force push ou reset destrutivo.
6. **Resolver conflitos por responsabilidade:** preservar backend/regra existente quando o conflito for apenas consequência de reorganização visual. Adaptar chamadas e contratos da V2 ao backend. Se um contrato precisar mudar, mapear callers, servidor, banco e testes antes de decidir.
7. **Revisar o diff resultante:** procurar SQL ou seleção de técnico dentro da UI; chamadas diretas ao banco pelo navegador; remoção de heartbeat, logout, pinagem, histórico ou endpoints; e caminhos que contornem `atribuir_ticket_aguardando()`/tratamento de Owner.
8. **Validar o comportamento:** executar as verificações da seção abaixo na branch integrada. Não considerar a integração pronta apenas porque a interface abre ou o código compila.
9. **Atualizar documentos:** registrar o estado real e os resultados em `estado_atual.md`, `regras_negocio.md`, `banco_dados.md` e `testes_e_problemas.md`. Atualizar este guia somente se o procedimento ou os contratos mudarem.
10. **Publicar:** após revisão e validação, abrir PR pela branch de integração para `main`, respeitando a proteção existente. Reconstruir o `.exe` somente a partir do código integrado/aprovado; manter `.env` ao lado do executável e fora do ZIP.

## Verificações de aceitação

### Fluxo e regras

- [ ] Login funciona para técnico e Supervisão; permissões/cargo continuam corretos.
- [ ] Técnico elegível com heartbeat recente aparece na rotação; heartbeat expirado remove elegibilidade após a janela de 15 segundos.
- [ ] Ticket novo é criado uma única vez, atribuído ao próximo técnico e avança a fila uma vez.
- [ ] Polling do mesmo ticket não duplica registros nem consome novas vezes após a atribuição.
- [ ] Sem técnico elegível, ticket fica `AGUARDANDO_TECNICO`.
- [ ] Ticket ativo aguardando, recebido de novo com técnico elegível, reusa sua atribuição, vira `PENDENTE` e avança a fila uma vez.
- [ ] Owner reconhecido como Supervisor é processado antes da reatribuição; histórico exibe `Supervisão` e a fila não avança por Supervisão.
- [ ] Owner técnico igual/diferente e Owner desconhecido seguem as regras do backend atual.
- [ ] Tickets fantasmas/ausentes do dashboard não são atribuídos por uma varredura global.
- [ ] Duas instâncias enviando o mesmo ticket simultaneamente não duplicam atribuição nem corrompem `fila_estado`.

### UI e operação

- [ ] Próximo e histórico refletem o banco compartilhado após atualização periódica.
- [ ] Botão Sair, fechamento da janela e retorno ao login limpam presença e cancelam callbacks.
- [ ] Supervisão não envia heartbeat técnico nem aparece como próximo.
- [ ] Fixar/desafixar a janela continua funcionando, salvo decisão explícita diferente.
- [ ] Falha de conexão não congela a UI nem deixa a aplicação em estado falso de presença.
- [ ] Servidor local e extensão continuam trocando dados pelos endpoints atuais.
- [ ] `.exe` recém-gerado abre no ambiente de distribuição com `.env` externo ao ZIP.

## Limites desta conferência inicial

Na conferência de 2026-10-14, o código da branch `carlos` passou por análise estática de sintaxe para as alterações de reavaliação. A integração real com a V2, o teste operacional com Neon/OTRS e um novo build ainda não foram confirmados. As verificações de aceitação acima são pendências, não resultados já obtidos.
