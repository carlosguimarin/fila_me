# Fila ME — Ambiente, `.env` e Executável

## 1. Desenvolvimento

Ambiente conhecido do Carlos:
- Windows 11
- Python 3.14.6
- VS Code
- PowerShell integrado do VS Code

Preferência de trabalho:
- código pelo VS Code;
- terminal para Git/comandos;
- instruções curtas e executáveis.

## 2. `.env`

Existem dois contextos:

### Execução Python

```text
fila_me\.env
```

### Executável PyInstaller

```text
fila_me\dist\.env
```

O segundo fica próximo ao executável.

Nenhum deles deve ser commitado.

## 3. PyInstaller

Executável conhecido:

```text
dist\FilaME.exe
```

A lógica de localização do `.env` considera a localização do executável quando o programa está congelado.

## 4. Atenção ao build

Se o código fonte mudar depois do build:

```text
dist/FilaME.exe
```

pode estar desatualizado.

Para uma release:
1. validar código;
2. validar testes;
3. integrar branch aprovada;
4. reconstruir executável;
5. colocar `.env` externamente;
6. testar executável limpo.

## 5. Distribuição

Plano futuro:
- GitHub Release;
- `FilaME.exe`;
- ZIP da extensão.

Nunca incluir:
- `.env`;
- senha;
- connection string;
- dados de usuários;
- dumps do banco.
