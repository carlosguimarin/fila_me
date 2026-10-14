# Fila ME — Regras de Negócio

## 1. Objetivo

Distribuir automaticamente novos tickets entre os técnicos que estão efetivamente trabalhando, mantendo uma fila centralizada e consistente entre vários computadores.

## 2. Participantes

### Técnico

Um usuário participa da fila quando:

```text
cargo = tecnico
AND ativo = true
AND trabalhando = true
AND ultimo_heartbeat >= CURRENT_TIMESTAMP - INTERVAL '15 seconds'
```

### Supervisão

Supervisor:
- pode possuir login;
- pode usar o Fila ME;
- pode ser identificado como Owner de um ticket;
- NÃO participa da fila automática;
- não altera a posição da fila ao assumir tickets.

## 3. Ordem da fila

A fila é um ciclo entre os técnicos atualmente trabalhando.

Exemplo:

```text
Carlos → Luís → Daniel → Carlos → Luís → ...
```

Se Daniel estiver ausente:

```text
Carlos → Luís → Carlos → Luís → ...
```

A lista efetiva de participantes é determinada no momento da atribuição.

## 4. O que significa "próximo"

"Próximo" é o técnico que receberia o próximo ticket novo de acordo com:
- estado central da fila;
- técnicos ativos;
- técnicos trabalhando.

Não é simplesmente o próximo ID de usuário.

## 5. Novo ticket

Quando um número de ticket ainda não existe em `tickets`:

1. registra o ticket;
2. identifica técnicos elegíveis;
3. seleciona o próximo técnico;
4. cria a atribuição inicial;
5. avança o estado da fila imediatamente.

Essa atribuição é provisória até que o Owner do OTRS possa ser observado.

## 6. Mesmo ticket

O mesmo número não pode ser registrado como um novo ticket novamente.

O navegador pode enviar o mesmo ticket repetidamente porque faz polling. Isso não deve criar várias atribuições.

A restrição `UNIQUE/PRIMARY KEY` no banco é parte da proteção.

Um ticket já conhecido, porém, pode continuar precisando de processamento. Se sua atribuição estiver em `AGUARDANDO_TECNICO`, quando ele for recebido novamente pela integração:

- o Owner recebido é processado primeiro;
- se for reconhecido como Supervisão, o chamado é confirmado como `SUPERVISAO` e não entra na fila técnica;
- se ainda permanecer `AGUARDANDO_TECNICO` e houver técnico elegível, recebe o próximo técnico da fila e passa para `PENDENTE`;
- a reavaliação não cria outro registro em `tickets` nem outra linha em `atribuicoes`.

Cada atribuição que sai de `AGUARDANDO_TECNICO` consome uma vez quando um técnico é escolhido. Tickets fantasma/removidos do OTRS não devem ser reintroduzidos manualmente nessa rotina.

## 7. Owner igual ao técnico inicial

Exemplo:

```text
Ticket 123
Atribuição inicial: Carlos
Owner OTRS: Carlos
```

Resultado:
- atribuição confirmada;
- Owner registrado;
- fila permanece como já havia sido avançada.

## 8. Owner diferente do técnico inicial

Exemplo:

```text
Ordem: Carlos → Luís → Daniel
Ticket novo:
atribuição inicial = Carlos

Luís assume manualmente no OTRS.
```

Resultado:
- Owner real = Luís;
- atribuição pode ser atualizada para representar o Owner real;
- isso é registrado para auditoria;
- NÃO alterar `fila_estado`;
- NÃO devolver a vez para Carlos;
- NÃO avançar a fila para Daniel por causa do Owner.

Assim, o próximo ticket continua seguindo a posição criada pela atribuição inicial.

### Regra crítica

Se Luís pegou um ticket que havia sido inicialmente atribuído a Carlos por uma necessidade interna, o próximo não deve virar Daniel apenas por isso.

## 9. Supervisor como Owner

Se o Owner for um usuário registrado como supervisor:

- registrar a ocorrência;
- classificar a atribuição como supervisão para exibição/histórico;
- não incluir supervisor na fila;
- não alterar `fila_estado`.

Na interface, o rótulo do histórico deve ser sempre `Supervisão`, mesmo que `owner_otrs` contenha o nome pessoal do supervisor. O nome real permanece armazenado no Owner para auditoria. O histórico mostra:

```text
#12345 → Supervisão
```

em vez de apresentar o técnico provisório como se ele tivesse sido o responsável final.

## 10. Owner desconhecido

Exemplo:

```text
Admin OTRS
```

Se o nome não corresponder a um usuário ativo registrado:

- gravar e exibir exatamente `Admin OTRS` em `owner_otrs`;
- substituir o nome desconhecido também nos dados enviados pela integração e nos logs;
- não inventar cargo;
- não assumir que é supervisor;
- preservar a atribuição existente.

Owners desconhecidos antigos também são apresentados como `Admin OTRS`. O Owner desconhecido, por si só, não muda a fila. Se a atribuição ainda estiver `AGUARDANDO_TECNICO`, a rotina separada de reavaliação pode atribuir o ticket a um técnico elegível depois de registrar o Owner; essa atribuição, e não a identidade desconhecida do Owner, é que consome a vez.

## 11. Nenhum técnico trabalhando

Se nenhum técnico elegível estiver trabalhando:

- o ticket continua registrado;
- a atribuição pode ficar sem técnico;
- status esperado: `AGUARDANDO_TECNICO`;
- a fila não deve inventar um participante.

Quando o mesmo ticket ativo for recebido novamente e já houver técnico elegível, ele pode sair de `AGUARDANDO_TECNICO` conforme a seção 6. Técnicos elegíveis são validados pelo heartbeat, com intervalo de envio aproximado de 5 segundos e validade de 15 segundos.

## 12. Logout

Quando técnico faz logout:

```text
trabalhando = false
```

Ele deixa de participar imediatamente das próximas seleções.

Isso pode gerar múltiplas atribuições consecutivas para o único técnico restante.

Isso NÃO é bug por si só.

## 13. Encerramento da aplicação

Fechar a aplicação deve retirar o técnico da fila.

Para a janela fixada:
- o atributo `-topmost` deve ser desativado no encerramento.

## 14. Primeiro bloqueio observado

- A extensão lê o valor da coluna `BLOQUEAR` separadamente do `PROPRIETÁRIO`.
- O estado atual (`bloqueado`/`desbloqueado`) é salvo em `tickets.status_bloqueio`, nunca em `atribuicoes.owner_otrs`.
- O primeiro valor explícito `bloqueado` marca o ticket como bloqueado confirmado e a interface usa verde na barra do chamado.
- A confirmação histórica fica associada ao número único em `tickets` e não é removida por leituras futuras de `desbloqueado`; se o chamado voltar para a fila, continua verde. O estado atual continua sendo exibido separadamente.
- Essa marca não identifica quem bloqueou e não altera Owner, atribuição ou posição da fila.
- O registro só é feito para tickets que já existem no banco, sem reintroduzir tickets ausentes do OTRS.

## 15. Exemplo completo

Estado:

```text
Carlos = trabalhando
Luís = trabalhando
Daniel = trabalhando

último = Daniel
```

Novo ticket A:
```text
→ Carlos
fila avança para Carlos
```

Luís assume A manualmente:
```text
Owner = Luís
fila NÃO muda
```

Novo ticket B:
```text
→ Luís
```

Se supervisor Mateus assumir B:
```text
Owner = Mateus
histórico = Supervisão
fila NÃO muda
```

Novo ticket C:
```text
→ Daniel
```

Esse comportamento é intencional.
