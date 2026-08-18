# Visão Geral da Arquitetura
O RevEla Analyzer segue a Clean Architecture com as seguintes camadas:
- **Domain:** Entidades Pydantic puras.
- **Application:** Use Cases e Orchestrator (Idempotentes).
- **Ingestion:** Serviços de descoberta e validação.
- **Infrastructure:** SQLAlchemy e Repositórios PostgreSQL.