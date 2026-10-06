# Fila ME — Fluxo Git e Colaboração

## 1. Branches

Conhecidas:

```text
main
carlos
luis
```

## 2. Regra

Carlos trabalha em:

```text
carlos
```

Luís trabalha em:

```text
luis
```

`main` é a branch de integração.

## 3. Sincronização de Luís com Carlos

Fluxo usado:

```powershell
git checkout luis
git fetch origin
git merge origin/carlos
```

Quando apareceu:

```text
Fast-forward
```

significava que `luis` estava atrás de `origin/carlos` sem commits divergentes, permitindo avançar diretamente.

Depois:

```powershell
git push origin luis
```

## 4. Desenvolvimento

Antes:

```powershell
git status
git fetch origin
```

Depois de atualizar:

```powershell
git add .
git commit -m "Descrição objetiva"
git push origin carlos
```

## 5. PR

Para integração:

```text
carlos → main
```

ou

```text
luis → main
```

somente após testes.

## 6. Histórico de PRs de teste

PRs antigos usados durante testes foram fechados:
- #3 Luís
- #4 Carlos

Não interpretar PR fechado como perda das alterações; o estado real deve ser conferido nas branches/commits.

## 7. Regra para IA

Nunca:
- resetar branch sem entender alterações;
- apagar commits;
- force push em `main`;
- descartar alterações locais para "resolver" conflito.

Antes de sugerir `reset --hard`, confirmar que o usuário quer descartar o conteúdo.

## 8. Commit

Commits devem explicar a mudança.

Exemplo:

```text
Corrige exibição de supervisão e janela fixada
```

Evitar commits genéricos como:

```text
update
fix
teste
mudanças
```

## 9. Estado local

O projeto foi trabalhado em:

```text
C:\Users\carlos\OneDrive - Ministerio Publico de Santa Catarina\Documents\work_space\fila_me
```

Ambiente de Luís conhecido:

```text
C:\Users\scanner\Documents\fila_me
```

Esses caminhos são específicos dos ambientes e não devem ser codificados na aplicação.
