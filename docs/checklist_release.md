# Fila ME — Checklist de Release

## Código

- [ ] branch de trabalho limpa ou alterações entendidas
- [ ] código revisado
- [ ] sem `.env`
- [ ] sem credenciais
- [ ] sem arquivos temporários
- [ ] imports funcionando
- [ ] testes passando

## Banco

- [ ] schema atualizado
- [ ] regras de fila confirmadas
- [ ] concorrência revisada
- [ ] não há reset destrutivo no fluxo normal

## OTRS

- [ ] número do ticket identificado
- [ ] Owner identificado
- [ ] polling funcionando
- [ ] ticket repetido não duplica
- [ ] Owner supervisor aparece como Supervisão
- [ ] Owner diferente não altera fila

## Usuários

- [ ] Técnico entra em `trabalhando`
- [ ] Técnico sai em logout
- [ ] encerramento remove técnico
- [ ] Supervisor não participa
- [ ] somente técnicos ativos e trabalhando entram na fila

## UI

- [ ] próximo exibido
- [ ] histórico atualizado
- [ ] Supervisão exibida corretamente
- [ ] botão Fixar funciona
- [ ] encerramento remove `topmost`

## Git

- [ ] commit descritivo
- [ ] push para branch
- [ ] PR revisado
- [ ] testes realizados
- [ ] main somente após aprovação

## Distribuição

- [ ] rebuild do PyInstaller
- [ ] `FilaME.exe` atualizado
- [ ] `.env` separado
- [ ] extensão atualizada
- [ ] pacote de release sem segredos
