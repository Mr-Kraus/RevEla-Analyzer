# Auditoria Expandida do Modelo Analítico (M03-F01)

Este documento atesta a viabilidade analítica do modelo relacional (construído no M02) para uso na camada de negócios.

## 1. Case (`case`)
* **Campos:** `id` (PK, UUID), `external_name` (str), `source_path` (str), `status` (Enum).
* **Relacionamentos:** `simulations` (1:N com SimulationRunModel).
* **Utilização Analítica:** Raiz agrupadoras para o `Comparison Engine`.
* **Limitações Conhecidas:** Não possui versionamento interno de alterações manuais.

## 2. SimulationRun (`simulation_run`)
* **Campos:** `id` (PK, UUID), `case_id` (FK), `analysis_type` (str), `simulated_years` (int).
* **Índices:** Indexado por `case_id` para *queries* rápidas de histórico.
* **Utilização Analítica:** Chave principal para buscar Topologia e Indicadores (Filtro base do M03).

## 3. System (`system`)
* **Relacionamentos:** `regions`, `buses`, `generators`, `transmission_lines`, `transformers` (Cascata 1:N).
* **Utilização Analítica:** Garante que a infraestrutura estudada pertence exclusivamente a uma rodada de simulação.

## 4. Region, Bus, Generator, TransmissionLine, Transformer
* **Estrutura Base:** Possuem `id` (PK), `external_id` (VARCHAR), e métricas de engenharia (`r_pu`, `x_pu`, `capacity_mva`, `failure_rate`).
* **Relacionamentos Topológicos:** As linhas e trafos possuem `from_bus_id` e `to_bus_id` garantindo a rastreabilidade do fluxo de potência.
* **Limitações:** A agregação de falhas (failure rate) em equipamentos compostos ainda depende de lógica em memória (Engine).

## 5. ReliabilityResult (`reliability_result`)
* **Campos:** Métricas flutuantes (`lolp`, `lole`, `epns`, etc.) atreladas a `simulation_run_id` e `bus_external_id`.
* **Índices:** Indexado em `is_global` e `bus_external_id` (velocidade nas agregações M03.9).
* **Utilização Analítica:** A estrutura "Flat" permite `SUM(epns)` via SQL puro.