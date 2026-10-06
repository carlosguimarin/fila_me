# Pacote de contexto compartilhado — Fila ME

Este diretório contém a base documental para permitir que diferentes IAs/ambientes entendam o mesmo projeto sem depender do histórico de um único chat.

## Conteúdo

```text
AGENTS.md
.github/
  copilot-instructions.md
  instructions/
docs/
  AI_CONTEXT.md
  arquitetura.md
  banco_dados.md
  checklist_release.md
  como_atualizar_contexto.md
  decisoes.md
  estado_atual.md
  git_fluxo.md
  historico_projeto.md
  matriz_de_conhecimento.md
  otrs_extensao.md
  regras_negocio.md
  seguranca.md
  testes_e_problemas.md
  ambiente_execucao.md
```

## Instalação no projeto

Copie o conteúdo deste pacote para a raiz do repositório `fila_me`.

Depois:

```powershell
git status
git add AGENTS.md .github docs
git commit -m "Adiciona contexto compartilhado e documentação do projeto"
git push origin carlos
```

Depois de testar, faça o PR para `main`.

## Observação

A documentação foi construída a partir do histórico técnico conhecido do projeto e deve ser conferida contra a branch atual antes da integração final.

Ela deliberadamente não contém:
- `.env`;
- `DATABASE_URL`;
- senhas;
- tokens;
- dados de autenticação.
