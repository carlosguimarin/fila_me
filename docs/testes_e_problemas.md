# Fila ME — Testes, Problemas e Soluções

Este documento registra problemas reais encontrados durante o desenvolvimento para evitar regressões.

## 1. Duplicação causada pelo polling

### Problema

A extensão consulta o OTRS repetidamente.

O mesmo ticket aparece em várias leituras.

### Risco

Criar várias linhas/atribuições para o mesmo ticket.

### Solução

`tickets.numero_ticket` é chave primária e o registro usa comportamento equivalente a:

```sql
ON CONFLICT DO NOTHING
```

`atribuicoes.numero_ticket` também é UNIQUE.

### Resultado

O mesmo ticket pode ser enviado repetidamente sem ser considerado novo.

---

## 2. Owner diferente alterando a fila

### Problema

Foi discutida/testada uma lógica que poderia usar o Owner real para recalcular a posição da fila.

Isso estava incorreto para a regra de negócio.

### Exemplo

Ordem:

```text
Carlos → Luís → Daniel
```

Ticket inicialmente atribuído a Carlos.

Luís assume manualmente.

### Comportamento correto

O próximo deve continuar sendo Luís.

### Solução

Owner posterior não altera `fila_estado`.

---

## 3. Supervisor aparecendo como técnico no histórico

### Problema

Quando supervisor assumia um ticket, o histórico ainda poderia exibir o técnico provisional.

### Solução

A consulta de histórico passou a apresentar:

```text
tipo_atribuicao = SUPERVISAO
→ "Supervisão"
```

Em vez de exibir o técnico provisional.

### Resultado observado

Testes com Mateus Marinho Furtado mostraram tickets exibidos como:

```text
→ Supervisão
```

---

## 4. Supervisor alterando a fila

### Problema

Foi necessário deixar explícito que supervisor não deve devolver/avançar turno.

### Solução

`atualizar_atribuicao_owner` atualiza classificação/Owner, mas não altera `fila_estado`.

---

## 5. Técnico fazendo logout

### Observação

Quando Carlos saiu e Luís permaneceu trabalhando, novos tickets foram atribuídos consecutivamente a Luís.

### Conclusão

Isso é comportamento esperado.

A fila considera apenas técnicos com:

```text
trabalhando = true
```

Não é obrigatório alternar entre pessoas que não estão trabalhando.

---

## 6. Botão Fixar

### Problema

Durante alterações da UI, o recurso de manter a janela acima das demais foi perdido temporariamente.

### Solução

Restaurado com:

```python
self.root.attributes("-topmost", True)
```

e botão:

```text
📌 Fixar
```

que muda para:

```text
📌 Fixado
```

No encerramento:

```python
self.root.attributes("-topmost", False)
```

### Resultado

Teste visual confirmou o estado `📌 Fixado`.

---

## 7. Driver de rede / ambiente de desenvolvimento

Fora do Fila ME em si, houve um problema de Cisco Secure Client que funcionava via Wi-Fi mas não via Ethernet.

Foram usados comandos como:
- `ipconfig /all`
- `route print`
- `nslookup`
- `tracert`
- `Test-NetConnection`
- `netsh interface ipv4 show interfaces`
- `netsh winhttp show proxy`
- `netcfg -d`

Também foram avaliadas propriedades do adaptador:
- Large Send Offload v2 IPv4/IPv6;
- Advanced EEE;
- Energy Efficient Ethernet.

O problema acabou resolvido instalando driver atualizado do fabricante.

Esse episódio é contexto de ambiente de desenvolvimento e não deve ser tratado como dependência funcional do Fila ME.

## 8. Teams

Houve tentativa de personalizar ícone do Microsoft Teams e manipular arquivos do pacote WindowsApps.

Houve Access Denied e tentativa de PowerShell/take ownership.

Esse trabalho não faz parte da arquitetura do Fila ME e não deve ser misturado às regras do projeto.

## 9. Estado dos testes

Os testes mais importantes confirmados:
- login/cadastro;
- identificação de cargo;
- técnico entrando na fila;
- técnico saindo da fila;
- atribuição automática;
- leitura do Owner pelo OTRS;
- reconhecimento de supervisor;
- histórico mostrando `Supervisão`;
- janela fixada;
- repetição de tickets sem duplicação;
- múltiplos técnicos trabalhando;
- cenário com somente um técnico trabalhando.

Testes de release ainda precisam ser repetidos após a consolidação final da documentação e código.

## 10. Reavaliação de tickets aguardando técnico

### Comportamento atual no código

`atribuir_ticket_aguardando(numero_ticket)` reavalia uma atribuição existente quando o servidor recebe o ticket pelos endpoints `/tickets` ou `/owner`. O Owner é processado antes da tentativa de reatribuição. Se a linha ainda estiver em `AGUARDANDO_TECNICO`, houver técnico elegível e o Owner/tipo não indicar Supervisão, a atribuição existente passa a `PENDENTE` para o próximo técnico e o ponteiro central da fila avança.

### Verificações necessárias antes da distribuição

Esse fluxo foi revisado estaticamente, mas o ciclo operacional ainda precisa ser confirmado com Neon e OTRS. Conferir pelo menos:

1. Sem técnico elegível, o ticket permanece `AGUARDANDO_TECNICO`.
2. Com técnico elegível, o mesmo ticket ativo muda para `PENDENTE` e recebe o próximo técnico.
3. Polling repetido não cria registros nem avança a fila de novo para o mesmo ticket depois que ele sai de `AGUARDANDO_TECNICO`.
4. Owner reconhecido como Supervisão é confirmado como `SUPERVISAO` e não consome vez.
5. Dois computadores enviando o mesmo ticket simultaneamente não duplicam a atribuição nem escolhem a mesma vez incorretamente.
6. Tickets removidos do OTRS/fantasmas não são reintroduzidos por uma varredura geral do banco.

Não considerar a mudança validada em produção apenas pela conferência de sintaxe.

## 11. Owner e bloqueio OTRS — correção de código pendente de validação operacional

Valores como `bloqueado`, `desbloqueado`, categorias e títulos de chamados foram observados em `owner_otrs` com a heurística antiga da última célula. A extensão foi alterada para extrair `PROPRIETÁRIO` e `BLOQUEAR` por cabeçalho e encaminhar o bloqueio separadamente. Validar a correspondência das colunas nos widgets `Chamados Novos` e `Chamados Abertos`; não corrigir registros antigos em massa nem inferir quem bloqueou pelo valor `bloqueado`.

O primeiro bloqueio observado agora é persistido em `tickets.bloqueio_confirmado`, com timestamp `bloqueado_em`, e a barra do painel usa verde. Leituras de `desbloqueado` não removem a confirmação. O fluxo ainda precisa de validação operacional com a extensão atualizada e o servidor conectado ao Neon.

## 12. Integração visual V2 na branch `luis` — 2026-10-14

- Testes isolados de `buscar_painel_visual()` e encerramento da janela: passaram com `python -m unittest tests.test_integracao_v2 -v`, usando mocks, sem acesso ao Neon.
- Execução manual relatada por Luís: a aplicação abriu, o servidor local iniciou em `127.0.0.1:8765` e recebeu polls da extensão. O ticket mostrado no log já existia (`Tickets novos: []`); esse teste não comprova atribuição de ticket novo nem o ciclo completo de presença/Owner.
- Compilação de sintaxe de `src/fila_me`: passou com `compileall`.
- Revisão estática: servidor local, extensão OTRS, schema e rotinas de atribuição/Owner não foram copiados do ZIP V2.
- Pendente: abrir a nova UI com as dependências instaladas, testar login/cadastro, tema, menus, histórico, presença, encerramento, Neon/OTRS e build do executável no ambiente operacional.
- Diferença identificada: a V1 altera `atribuicoes.tecnico` quando outro técnico assume, enquanto a documentação o descreve como atribuição provisória separada do Owner. Por decisão do responsável, o comportamento funcional da V1 foi mantido nesta integração visual.
