# Fila ME — Instruções para agentes de IA

## 1. Objetivo

O Fila ME é uma aplicação desktop em Python/Tkinter que organiza a distribuição de tickets do OTRS entre técnicos que estão efetivamente trabalhando.

A aplicação roda localmente em cada computador da equipe, enquanto o estado compartilhado da fila e o histórico de tickets ficam centralizados em PostgreSQL hospedado no Neon.

Há também uma extensão de navegador que lê o dashboard do OTRS e envia para a aplicação local o número dos tickets e o Owner identificado no DOM.

Este arquivo é uma instrução operacional para agentes de IA. A documentação detalhada fica em `docs/`.

## 2. Fonte de verdade

Ao trabalhar no projeto, considere esta ordem:

1. Código existente na branch atual.
2. Banco/schema e comportamento efetivamente implementados.
3. `docs/regras_negocio.md` para regras funcionais.
4. `docs/decisoes.md` para decisões já tomadas.
5. `docs/estado_atual.md` para o estado conhecido do projeto.
6. Demais documentos em `docs/` para arquitetura, testes e operação.
7. Histórico de conversas somente como contexto complementar.

Não invente comportamento que não esteja documentado ou implementado.

Se código e documentação divergirem, NÃO altere silenciosamente a regra de negócio. Informe a divergência e proponha a correção.

## 3. Regra crítica da fila

A atribuição inicial/provisional de um novo ticket é quem avança a fila.

Se OTRS posteriormente mostrar outro Owner:

- mesmo técnico inicialmente atribuído: confirma a atribuição;
- outro técnico registrado: registra o Owner real, mas NÃO altera a posição da fila;
- supervisor: registra como supervisão, mas NÃO altera a posição da fila;
- Owner desconhecido: registra `owner_otrs`, sem alterar a fila.

NUNCA implemente lógica que recalcula ou devolve o turno com base no Owner posterior sem uma decisão explícita do responsável pelo projeto.

## 4. Técnicos elegíveis

Somente usuários que atendam simultaneamente a:

- `cargo = 'tecnico'`
- `ativo = true`
- `trabalhando = true`

participam da seleção automática.

Supervisores não participam da fila automática.

Quando um técnico entra na tela principal, seu estado `trabalhando` passa para `true`.

Quando faz logout ou encerra a aplicação, seu estado passa para `false`.

Consequência intencional: se somente um técnico estiver trabalhando, vários tickets novos consecutivos podem ser atribuídos a ele.

## 5. Tickets

`numero_ticket` é o identificador único do ticket.

O navegador pode enviar o mesmo ticket a cada ciclo de polling. Isso é esperado.

O banco deve impedir que o mesmo número seja registrado novamente.

Um ticket que reapareça semanas ou meses depois continua sendo o mesmo ticket e NÃO deve ser tratado como novo somente por ter reaparecido.

## 6. Concorrência

As instâncias do Fila ME podem estar rodando simultaneamente em vários computadores.

A decisão de quem recebe o próximo ticket deve acontecer no banco central, e não em uma cópia local da aplicação.

A operação de registrar ticket + selecionar técnico + avançar o estado da fila deve permanecer transacional e protegida contra concorrência.

A linha de `fila_estado` é bloqueada com `FOR UPDATE` durante a decisão.

## 7. Segurança

Nunca:

- commitar `.env`;
- expor `DATABASE_URL`;
- colocar senha do banco no código;
- copiar credenciais reais para documentação;
- sugerir colocar segredos no GitHub.

O `.gitignore` já deve manter `.env` fora do Git.

Senhas de usuários do Fila ME são armazenadas usando PBKDF2-HMAC-SHA256 com salt aleatório.

## 8. Fluxo Git

O desenvolvimento normal ocorre em branch de trabalho.

Branches conhecidas:
- `main`
- `carlos`
- `luis`

`main` é protegido e a integração final ocorre por Pull Request.

Não fazer force push em `main`.

Antes de editar:
- verificar `git status`;
- sincronizar a branch;
- preservar alterações locais;
- entender a documentação relevante.

Depois de editar:
- testar;
- revisar diff;
- commit descritivo;
- push da branch;
- PR quando aplicável.

## 9. Não fazer mudanças amplas sem necessidade

Prefira alterações pequenas, localizadas e compatíveis com o código existente.

Não refatore arquitetura inteira só para implementar uma funcionalidade pequena.

Não altere schema, regras de fila ou integração OTRS sem atualizar a documentação correspondente.

## 10. Documentação contextual

Não é necessário ler todos os documentos para cada alteração.

Use:
- fila/atribuição → `docs/regras_negocio.md`, `docs/banco_dados.md`, `docs/decisoes.md`;
- Python/Tkinter → `docs/arquitetura.md`, `docs/estado_atual.md`;
- OTRS/extensão → `docs/otrs_extensao.md`;
- testes/regressões → `docs/testes_e_problemas.md`;
- Git → `docs/git_fluxo.md`;
- build/executável → `docs/ambiente_execucao.md`;
- mudança de segurança → `docs/seguranca.md`.

Para uma alteração estrutural grande, consulte `docs/AI_CONTEXT.md` primeiro.

## 11. Regra de trabalho com o usuário

O usuário prefere instruções:
- diretas;
- objetivas;
- em passos;
- com comandos completos;
- sem repetir explicações desnecessárias.

Se uma sequência tiver vários passos e o usuário disser que executou somente um, considere os demais NÃO executados e retome a partir do ponto correto.

