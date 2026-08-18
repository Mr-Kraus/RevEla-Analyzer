# Regras de Dependência
1. A camada de `Domain` não pode importar nada de fora (SQLAlchemy, FastAPI).
2. `Application` depende apenas de abstrações (Interfaces) e do `Domain`.
3. `Infrastructure` implementa as interfaces do `Domain`.