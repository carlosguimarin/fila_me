# FILA ME

Aplicativo desktop para acompanhar a distribuição de chamados entre os técnicos. O aplicativo usa o PostgreSQL central configurado pela equipe e uma extensão de navegador para ler o dashboard do OTRS.

## Baixar e iniciar

1. Baixe `FilaME.zip` na área de arquivos da versão e extraia `FilaME.exe` para uma pasta.
2. Obtenha o arquivo `.env` da equipe responsável e coloque-o na mesma pasta do `FilaME.exe`. Ele contém a conexão privada com o banco e não é distribuído dentro do ZIP nem deve ser publicado no GitHub.
3. Execute `FilaME.exe` e entre com seu login.

## Instalar a extensão do OTRS

A extensão pode ser usada em qualquer navegador que ofereça suporte a extensões **Manifest V3** com service worker e permita carregar uma extensão local. O navegador precisa estar aberto no OTRS para a leitura funcionar. A extensão monitora `https://helpdesk.mpsc.mp.br/otrs/` e conversa com o FILA ME em `127.0.0.1:8765`.

1. Baixe e extraia `FilaME-Extensao.zip` para uma pasta permanente. Não apague essa pasta depois de carregar a extensão.
2. Abra a página de gerenciamento de extensões do navegador.
3. Ative o modo de desenvolvedor e escolha **Carregar sem compactação** (ou a opção equivalente no navegador).
4. Selecione a pasta extraída que contém `manifest.json`.
5. Acesse o dashboard do OTRS e autorize a extensão a acessar o site, se o navegador solicitar.

O pacote da extensão contém os arquivos necessários para carregamento local. Em navegadores sem suporte a Manifest V3 ou a extensões locais, a extensão não será compatível.

## Configurar as colunas do OTRS

Nos widgets **Chamados Novos** e **Chamados Abertos**, configure a exibição das duas colunas:

- `PROPRIETÁRIO` — nome do técnico ou responsável no OTRS;
- `BLOQUEAR` — estado `bloqueado` ou `desbloqueado`.

A coluna `BLOQUEAR` precisa estar visível nos dois widgets para que o FILA ME leia o estado corretamente. O proprietário e o estado de bloqueio são informações separadas.

## Atualizar a extensão

Extraia a nova versão por cima de uma pasta nova ou atualizada, abra o gerenciador de extensões e use **Recarregar** na extensão Fila ME. Mantenha o aplicativo desktop aberto enquanto usa o dashboard.

## Arquivos desta versão

- `FilaME.zip` — contém somente `FilaME.exe`; o `.env` é fornecido separadamente pela equipe.
- `FilaME-Extensao.zip` — arquivos da extensão para carregar no navegador.
- `docs/notas_release.md` — resumo das mudanças e instruções de publicação.
