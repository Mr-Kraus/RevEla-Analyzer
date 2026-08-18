# M02 - Dataset Catalog & Classification (ReLeVa Parser)

Este documento reflete a engenharia reversa dos arquivos brutos exportados pelo ReLeVa (em conformidade com o CA-01).

## 1. TEMPLATE_SETTINGS
* **Arquivo:** `Template Settings.csv`
* **Categoria:** `CONFIGURATION`
* **Estrutura:** Bloco único de chave e valor, separados por `;`.
* **Características Reais Identificadas:**
  * As chaves não possuem um cabeçalho fixo no topo.
  * O delimitador é `;` seguido de múltiplos `;` vazios.
  * Valores booleanos aparecem como `true`/`false`.
  * Valores numéricos decimais utilizam `.` (ponto).
* **Campos Identificados (Exemplos):** `NUM_MAX_YEARS`, `ANALYSIS_TYPE`, `V_MIN`, `V_MAX`.

## 2. TEMPLATE_SYSTEM
* **Arquivo:** `Template System.csv`
* **Categoria:** `TOPOLOGY`
* **Estrutura:** Multi-blocos sequenciais baseados em *Flags C-Style*.
* **Características Reais Identificadas:**
  * Cada bloco inicia com uma flag declarativa (ex: `<BARRAS>`).
  * Imediatamente abaixo da flag, há um número inteiro indicando a quantidade de elementos que se seguem (ex: `95`).
  * Duas linhas de cabeçalho delimitam os nomes das colunas e as unidades de medida (ex: `ID;NAME;SLACK...` seguido de `;;;pu;kV...`).
  * O bloco de dados real é encapsulado pelas flags `<VAL>` e `<\\VAL>`.
* **Sub-blocos Encontrados:**
  * `<CARGAP>` (Carga)
  * `<CLCONS>` (Classe de Consumo)
  * `<CLGERA>` (Classe de Geração)
  * `<HIDRO>` (Hidrelétrica)
  * `<TERMI>` (Térmica)
  * `<EOLIC>` (Eólica)
  * `<SOLAR>` (Solar)
  * `<LINHAS>` (Linhas de Transmissão)
  * `<TRAFOS>` (Transformadores)
  * `<BARRAS>` (Barras/Nós)

## 3. FINAL_RELIABILITY_INDICES
* **Arquivo:** `Final Reliability Indices.csv`
* **Categoria:** `RESULTS_GLOBAL`
* **Estrutura:** Multi-blocos de resultados agregados.
* **Características Reais Identificadas:**
  * Metadados no topo (`Simulated years;100`).
  * Separação de blocos por strings textuais literais (ex: `Total Global Indices:`, `Global Indices by Failure Type:`, `Main System Indices by Region:`).
  * Valores inválidos reportados em C++ nativo como `-nan(ind)`.
  * Dados em notação científica nativa (ex: `1.7231251677990434E-02`).