# Fila ME — Segurança

## 1. Segredos

Nunca versionar:
- `DATABASE_URL`;
- pooled connection string;
- senhas;
- tokens;
- cookies;
- credenciais OTRS.

`.env` deve permanecer no `.gitignore`.

## 2. Senhas dos usuários

A aplicação não armazena senha em texto puro.

Algoritmo:

```text
PBKDF2-HMAC-SHA256
600.000 iterações
salt aleatório de 16 bytes
```

Formato lógico:

```text
pbkdf2_sha256$ITERACOES$SALT_HEX$HASH_HEX
```

## 3. Autenticação

O fluxo:

```text
email
  ↓
buscar usuário
  ↓
verificar ativo
  ↓
verificar senha
  ↓
retornar sessão lógica
```

O retorno conhecido inclui:
- id;
- nome;
- email;
- cargo;
- ativo;
- trabalhando.

## 4. Banco

A aplicação desktop possui acesso ao banco central.

Por isso:
- não imprimir connection string;
- não logar senha;
- não criar endpoint HTTP que devolva credenciais;
- manter servidor local limitado ao necessário.

## 5. Extensão

A extensão acessa o OTRS porque precisa ler a página.

Ela não deve receber a senha do banco.

## 6. Logs

Logs de diagnóstico podem mostrar:
- número de ticket;
- Owner;
- erros técnicos.

Evitar mostrar:
- senha;
- connection string;
- dados sensíveis desnecessários.

## 7. Futuro

Antes de produção real, considerar:
- princípio de menor privilégio no banco;
- usuário de banco específico para aplicação;
- TLS obrigatório;
- validação de payload local;
- proteção contra requests arbitrários ao servidor local;
- rotação de credenciais;
- auditoria.
