# M02 - Data Contracts (Especificações dos Parsers)

Em conformidade com o CA-02, estas são as regras absolutas (state machines) para a criação dos parsers em Python no M02.7.

## Contrato 1: `TemplateSystemParser`
**Modo de Leitura:** Sequencial (State Machine).
**Regra de Transição:**
1. Ler linha a linha.
2. Se a linha iniciar com `<` e fechar com `>`, extrair a string interna como o ESTADO ATUAL (ex: `BARRAS`).
3. Ler a próxima linha como um Inteiro ($N$). Este é o contador de elementos esperados.
4. Ignorar linhas até encontrar a flag de abertura de dados `<VAL>`.
5. Extrair $N$ linhas seguintes separando por `;`.
6. O loop encerra ao encontrar a flag `<\VAL>`.

## Contrato 2: `TemplateSettingsParser`
**Modo de Leitura:** Key-Value (Dicionário Simples).
**Regra de Transição:**
1. Ler linha a linha, ignorando vazias.
2. Dividir por `;`.
3. O índice `[0]` é a chave (`NUM_MAX_YEARS`), o índice `[1]` é o valor (`10000`).
4. Cast estrito: se `true/false`, virar Booleano. Se numérico, float/int.

## Contrato 3: `ReliabilityIndicesParser`
**Modo de Leitura:** Padrão de Busca por Âncora (Regex/Sub-string).
**Regra de Transição:**
1. Localizar âncoras (`Total Global Indices:`, `Main System Indices by Region:`).
2. Ler a tabela logo abaixo das âncoras.
3. Conversão Crítica: Substituir a string literal do C++ `-nan(ind)` pelo tipo `float('nan')` nativo do Python (ou nulo no banco) antes do Pydantic processar.