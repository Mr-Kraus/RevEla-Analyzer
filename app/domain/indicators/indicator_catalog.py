from dataclasses import dataclass
from app.domain.value_objects.indicator_vo import IndicatorScope, IndicatorUnit, IndicatorCategory

@dataclass(frozen=True)
class IndicatorDefinition:
    code: str
    name: str
    description: str
    unit: IndicatorUnit
    category: IndicatorCategory

class IndicatorCatalog:
    """Registro Oficial e Imutável de todos os indicadores suportados pelo RevEla."""
    
    _CATALOG = {
        "LOLP": IndicatorDefinition(
            code="LOLP",
            name="Loss of Load Probability",
            description="Probabilidade de perda de carga no sistema.",
            unit=IndicatorUnit.PERCENTAGE,
            category=IndicatorCategory.ADEQUACY
        ),
        "LOLE": IndicatorDefinition(
            code="LOLE",
            name="Loss of Load Expectation",
            description="Expectativa de perda de carga.",
            unit=IndicatorUnit.HOURS_PER_YEAR,
            category=IndicatorCategory.ADEQUACY
        ),
        "EPNS": IndicatorDefinition(
            code="EPNS",
            name="Expected Power Not Supplied",
            description="Potência esperada não suprida.",
            unit=IndicatorUnit.MW,
            category=IndicatorCategory.ADEQUACY
        ),
        "EENS": IndicatorDefinition(
            code="EENS",
            name="Expected Energy Not Supplied",
            description="Energia esperada não suprida.",
            unit=IndicatorUnit.MWh_PER_YEAR,
            category=IndicatorCategory.ADEQUACY
        ),
        "LOLF": IndicatorDefinition(
            code="LOLF",
            name="Loss of Load Frequency",
            description="Frequência de ocorrência de perda de carga.",
            unit=IndicatorUnit.OCCURRENCES_PER_YEAR,
            category=IndicatorCategory.ADEQUACY
        ),
        "LOLD": IndicatorDefinition(
            code="LOLD",
            name="Loss of Load Duration",
            description="Duração média de uma ocorrência de perda de carga.",
            unit=IndicatorUnit.HOURS_PER_YEAR,
            category=IndicatorCategory.ADEQUACY
        ),
        "LOLC": IndicatorDefinition(
            code="LOLC",
            name="Loss of Load Cost",
            description="Custo esperado associado à perda de carga.",
            unit=IndicatorUnit.DOLLARS_PER_YEAR,
            category=IndicatorCategory.ECONOMIC
        )
    }

    @classmethod
    def get(cls, code: str) -> IndicatorDefinition:
        if code not in cls._CATALOG:
            raise ValueError(f"Indicador desconhecido: {code}")
        return cls._CATALOG[code]

    @classmethod
    def get_all(cls) -> list[IndicatorDefinition]:
        return list(cls._CATALOG.values())