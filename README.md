# Sistema Bancário em Python — versão otimizada

Sistema bancário educacional executado no terminal, com cadastro de usuários, criação de contas, depósitos, saques, extrato e listagem de contas.

## Melhorias aplicadas

- **Precisão financeira:** valores monetários passaram de `float` para `Decimal`, evitando erros de arredondamento.
- **Validação de entrada:** CPF, data de nascimento, endereço, valores e números de conta recebem validação e mensagens claras.
- **Código modular:** funções auxiliares para conversão monetária, normalização de CPF, busca de usuário e leitura de valores reduzem duplicação.
- **Desempenho:** a listagem de contas cria um índice de nomes por CPF uma única vez, em vez de fazer uma busca linear para cada conta.
- **Manutenção:** funções de negócio retornam resultados explícitos, o que facilita testes e futura evolução para uma interface gráfica ou API.
- **Robustez:** o programa trata `EOFError` e `KeyboardInterrupt` para sair sem traceback; a criação de conta só incrementa o número quando realmente é concluída.
- **Compatibilidade com o desafio:** as assinaturas com `/` e `*` de `depositar`, `sacar` e `exibir_extrato` foram preservadas.

## Estrutura

```text
Otimizando o Sistema Bancário com Funções Python/
├── README.md
└── desafio/
    ├── desafio.py
    └── test_desafio.py
```

## Como executar

Na pasta `desafio`:

```bash
python3 desafio.py
```

## Como testar

```bash
python3 -m unittest -v test_desafio.py
```

Os dados permanecem apenas em memória durante a execução. Para um sistema de produção, o próximo passo seria adicionar persistência em banco de dados, autenticação, auditoria e transações.

## Regras atuais

A agência é fixa em `0001`. Cada conta recebe um número sequencial. São permitidos até três saques por dia, com limite de R$ 500,00 por saque e validação de saldo suficiente.
