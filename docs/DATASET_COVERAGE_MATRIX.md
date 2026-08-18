# Matriz de Cobertura de Datasets (M02-F00)

Esta matriz rastreia a capacidade do pipeline de ingestão de ler os blocos estruturais extraídos da engenharia reversa dos arquivos originais do ReLeVa.

## 1. Template Settings.csv
| Parâmetro | Mapeado no DTO? | Destino no Domínio |
| :--- | :--- | :--- |
| `NUM_MAX_YEARS` | ✔️ Sim | `SimulationRun.simulated_years` |
| `ANALYSIS_TYPE` | ✔️ Sim | `SimulationRun.analysis_type` |
| `CONFIDENCE` | ✔️ Sim | `SimulationRun.confidence_level` |
| `CE_*` (Convergência) | ✔️ Sim | `SimulationRun.convergence_configuration` (JSON) |

## 2. Template System.csv
| Bloco (C++) | Descrição | Status do Parser/Mapper | Destino no Domínio |
| :--- | :--- | :--- | :--- |
| `<BARRAS>` | Nós do sistema | ✔️ Mapeado | `BusModel` |
| `<CLGERA>` | Classes de Geração | ✔️ Mapeado | `GeneratorModel` |
| `<LINHAS>` | Linhas de Transmissão | ✔️ Mapeado | `TransmissionLineModel` |
| `<TRAFOS>` | Transformadores | ✔️ Mapeado | `TransformerModel` |
| `<TERMI>` | Termelétricas (Instâncias) | ⏳ Pendente (M03) | - |
| `<HIDRO>` | Hidrelétricas | ⏳ Pendente (M03) | - |
| `<SOLAR>` | Plantas Solares | ⏳ Pendente (M03) | - |