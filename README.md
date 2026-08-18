# RevEla Analyzer

Sistema de orquestração, normalização e análise gráfica para dados do software ReLeVa.

## Milestone 01 - Fundação Arquitetural
Este projeto implementa uma Clean Architecture estrita para o módulo de Ingestão:
1. **Discovery:** Varre a pasta do caso (ex: C01).
2. **Validation:** Verifica a integridade contra o `DatasetRegistry`.
3. **Registration:** Salva Case e SourceFiles com hashes SHA-256 no PostgreSQL.

## Executando os Testes
Para rodar a suíte completa (Unidade e Integração):
```bash
python -m pytest tests/ -v