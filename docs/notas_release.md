# Notas para a próxima versão

## Mudanças

- Ícone da coruja aplicado ao aplicativo desktop, ao executável e à extensão do navegador.
- Histórico de atribuições exibe nome, número e estado do bloqueio separadamente.
- A extensão lê `PROPRIETÁRIO` e `BLOQUEAR` em colunas distintas nos widgets do OTRS.
- O estado de bloqueio é acompanhado sem substituir o nome do Owner.
- README atualizado com instalação do aplicativo e da extensão e configuração das colunas do OTRS.

## Pacotes preparados

- `dist/FilaME.zip`: contém apenas `FilaME.exe`.
- `dist/FilaME-Extensao.zip`: pacote da extensão para carregamento local.
- O arquivo `.env` fica fora dos pacotes públicos e deve ser entregue separadamente de forma segura.

## Publicação

1. Publique o `FilaME.zip` e o `FilaME-Extensao.zip` como arquivos da versão.
2. Não publique nem inclua o `.env`.
3. Inclua o conteúdo deste arquivo como notas da versão.
4. A versão do produto ainda precisa ser definida antes de criar a publicação; o manifesto da extensão atualmente declara `0.1.0`.

