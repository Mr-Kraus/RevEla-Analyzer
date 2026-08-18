# M02 - Persistence Mapping (DTO -> Domain)

Este documento audita as saídas atuais dos nossos Normalizers e mapeia como elas se relacionam com as Entidades do Domínio para persistência, conforme exigido na Fase 1 do fechamento do M02.

## 1. SettingsNormalizer
**Campos Produzidos (Canonical DTO):**
* `simulated_years` (int)
* `analysis_type` (str)
* `system_representation` (str)

**Destino de Persistência:**
* Entidade: `SimulationRun`
* Relacionamento: Pertence diretamente a um `Case`.

## 2. ReliabilityIndicesNormalizer
**Campos Produzidos (Canonical DTO):**
* `global_indices`: Dicionário contendo `lolp`, `lole`, `epns`, `eens`, `lolf`, `lold`, `lolc` (floats).
* `bus_indices`: Lista de dicionários contendo `bus_external_id` e os mesmos 7 indicadores acima.

**Destino de Persistência:**
* Entidade: `ReliabilityResult` (Nova entidade a ser validada na Fase 3).
* Relacionamentos: 
  * Os índices globais vinculam-se à `SimulationRun`.
  * Os índices por barra vinculam-se a uma `Bus` específica e a uma `SimulationRun`.

## 3. SystemNormalizer (Topologia)
**Campos Produzidos (Canonical DTO):**
* `regions`: Lista com `external_id`, `name`.
* `buses`: Lista com `external_id`, `name`, `voltage_kv`, `region_external_id`.
* `generation_classes`: Lista com `external_id`, `name`, `failure_rate_percent`, `repair_time_hours`, `nominal_capacity_mw`.
* *(Pendente de Extração no Normalizer)*: `generators`, `transmission_lines`, `transformers`.

**Destino de Persistência:**
* Entidades: `System`, `Region`, `Bus`, `GenerationClass`, `Generator`, `TransmissionLine`, `Transformer`.
* Relacionamentos:
  * `System` pertence à `SimulationRun`.
  * `Region`, `Bus`, `Line`, `Transformer`, `Generator` pertencem ao `System`.
  * `Bus` vincula-se à `Region`.
  * Equipamentos (`Generator`, `Line`, `Transformer`) vinculam-se a `Bus` (from_bus / to_bus).