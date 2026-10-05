# Fila ME — Contexto Completo para IA

## Finalidade deste documento

Este é o ponto de entrada recomendado quando uma IA nova precisa entender o Fila ME.

O projeto foi desenvolvido de forma incremental e várias decisões importantes nasceram de testes reais. O objetivo desta documentação é evitar que uma IA futura "simplifique" uma regra que já foi testada ou repita um problema já resolvido.

## Documentos

- `../AGENTS.md` — regras de trabalho para agentes.
- `../.github/copilot-instructions.md` — instruções para Copilot.
- `estado_atual.md` — o que está funcionando e o que está pendente.
- `regras_negocio.md` — regras funcionais definitivas.
- `arquitetura.md` — componentes e responsabilidades.
- `banco_dados.md` — schema e lógica transacional.
- `otrs_extensao.md` — integração com OTRS/browser.
- `testes_e_problemas.md` — testes feitos, problemas encontrados e resultados.
- `decisoes.md` — decisões que não devem ser revertidas sem discussão.
- `git_fluxo.md` — colaboração entre Carlos e Luís.
- `ambiente_execucao.md` — execução Python, `.env` e PyInstaller.
- `seguranca.md` — segredos e autenticação.
- `historico_projeto.md` — evolução conhecida do projeto.

## Como uma IA deve começar

Para uma tarefa pequena, não é necessário ler tudo.

Use o documento correspondente à área da alteração.

Para uma alteração que envolva fila + banco + OTRS, leia pelo menos:
1. `regras_negocio.md`
2. `banco_dados.md`
3. `otrs_extensao.md`
4. `decisoes.md`

Para uma tarefa de arquitetura ampla, leia todos os documentos relevantes.

## Estado de confiança

Esta documentação combina:
- comportamento confirmado em código;
- decisões confirmadas em testes;
- histórico de desenvolvimento;
- detalhes de ambiente informados durante o desenvolvimento.

Quando um detalhe não puder ser verificado diretamente no código, ele deve ser tratado como "histórico/contexto" e não como prova de que o estado atual da branch é exatamente aquele.

A documentação deve ser atualizada quando o projeto mudar.
