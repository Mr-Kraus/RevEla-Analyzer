# M02 - Entity Mapping & Revisão do Modelo (M01 vs Realidade)

Em conformidade com o CA-04, analisamos a topologia real do ReLeVa contra o nosso modelo criado no M01.

## Avaliação do Modelo M01

**O Modelo M01 está adequado, MAS PRECISA DE EXPANSÕES.**
Ao ler o `Template System.csv`, observamos que a topologia de Geração é ramificada. O ReLeVa não exporta apenas "Geradores", ele exporta:
- Térmicas (`<TERMI>`)
- Hidrelétricas (`<HIDRO>`)
- Solares (`<SOLAR>`)
- Eólicas (`<EOLIC>`)

Além disso, todas elas referenciam uma Classe de Geração (`<CLGERA>`), onde residem de fato as taxas de falha (`FRATE`) e tempo de reparo (`MTTR`), e não no equipamento em si.

**Ação Exigida para Refatoração (M02.5):**
1. O Domain `Generator` atual precisa ser generalizado ou decomposto.
2. A entidade `GenerationClass` (Classe de Geração) precisa ser adicionada ao Domain.
3. Precisamos adicionar suporte ao tratamento numérico de `-nan(ind)` nos DTOs de resultados.