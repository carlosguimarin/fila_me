# Estado Atual do Fila ME

> Documento de acompanhamento. Atualizar sempre que uma funcionalidade importante mudar.

## 1. Stack conhecida

- Python
- Tkinter para interface desktop
- PostgreSQL
- Neon como banco central
- extensão de navegador em JavaScript
- comunicação da extensão com servidor local Python via `127.0.0.1:8765`
- OTRS como sistema de tickets
- PyInstaller para gerar executável

## 2. Componentes conhecidos

Estrutura relevante:

```text
src/fila_me/
├── app.py
├── database/
│   ├── banco.py
│   └── autenticacao.py
├── ...
```

Também existem:
- `docs/`
- `tests/`
- arquivos da extensão do navegador
- `requirements.txt`

A estrutura exata deve ser confirmada na branch antes de criar novos caminhos.

## 3. Funcionalidades confirmadas durante desenvolvimento

### Autenticação

- Login por e-mail e senha.
- Cadastro de usuário.
- Cargo:
  - Técnico
  - Supervisão
- Usuário pode estar ativo/inativo.
- Técnico possui estado de trabalho (`trabalhando`).

### Tela principal

- Nome do usuário no cabeçalho.
- Cargo exibido.
- Botão `Sair`.
- Botão `📌 Fixar` / `📌 Fixado`.
- Indicador `Próximo`.
- Histórico das últimas atribuições.
- Atualização periódica do estado.
- Técnico entra como trabalhando ao abrir a tela.
- Técnico sai da fila ao fazer logout/encerrar.

### Fila

- Estado centralizado no Neon.
- Somente técnicos ativos com `trabalhando = TRUE` e heartbeat válido por 15 segundos participam.
- Atribuição inicial avança a fila.
- Owner posterior não corrige a posição da fila.
- Uma atribuição existente em `AGUARDANDO_TECNICO` pode ser reavaliada quando o ticket volta a ser recebido pela integração. O Owner é processado primeiro; Supervisão não entra na fila técnica.

### OTRS

- Extensão lê o dashboard.
- Número do ticket e Owner são enviados.
- Polling atual: aproximadamente 5 segundos.
- A aplicação local recebe os dados.
- A leitura do Owner pode estar incorreta em algumas linhas; valores como `bloqueado`, `desbloqueado` e assunto de chamado já apareceram em `owner_otrs`.

### Histórico

A tela foi ajustada para exibir:
- nome do técnico quando aplicável;
- `Supervisão` quando a atribuição foi reconhecida como supervisão;
- `Aguardando técnico` quando não havia técnico trabalhando.

## 4. Build

Foi gerado e testado um executável com PyInstaller:

```text
dist/FilaME.exe
```

O executável utiliza um `.env` ao lado dele quando congelado.

Importante: alterações posteriores ao build tornam o `.exe` potencialmente desatualizado. Não considerar o executável como equivalente automático ao código-fonte.

## 5. Pendências/conferências

Antes de uma release final, conferir:
- todos os commits da branch `carlos` foram integrados;
- branch `luis` está sincronizada;
- documentação foi commitada;
- testes automatizados existem e estão atualizados;
- testes manuais críticos foram repetidos;
- `main` recebeu somente o que foi aprovado;
- executável foi reconstruído após o último código aprovado;
- extensão distribuída corresponde ao código aprovado.

A sintaxe do fluxo recente de reavaliação foi conferida, mas sua operação com Neon/OTRS e o ciclo completo ainda precisam ser validados antes de distribuir o executável.

## 6. Integração da V2 de interface

Antes de integrar uma mudança grande de UI, seguir `integracao_v2.md`. A UI pode mudar de organização e aparência, mas deve preservar os contratos de banco, fila, presença, Owner, Supervisão, servidor local e encerramento descritos nos documentos de regras e arquitetura.
