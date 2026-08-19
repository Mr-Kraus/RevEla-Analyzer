from dataclasses import dataclass
from typing import List
from app.domain.value_objects.indicator_vo import IndicatorScope, IndicatorUnit, IndicatorCategory

@dataclass(frozen=True)
class IndicatorDefinition:
    code: str
    name: str
    description: str
    unit: IndicatorUnit
    category: IndicatorCategory
    allowed_scopes: List[IndicatorScope] 

class IndicatorCatalog:
    _CATALOG = {
        "LOLP": IndicatorDefinition(
            code="LOLP",
            name="Loss of Load Probability",
            description="Probabilidade de perda de carga.",
            unit=IndicatorUnit.PERCENTAGE,
            category=IndicatorCategory.ADEQUACY,
            allowed_scopes=[IndicatorScope.GLOBAL, IndicatorScope.REGION, IndicatorScope.BUS]
        ),
        "LOLE": IndicatorDefinition(
            code="LOLE",
            name="Loss of Load Expectation",
            description="Expectativa de perda de carga.",
            unit=IndicatorUnit.HOURS_PER_YEAR,
            category=IndicatorCategory.ADEQUACY,
            allowed_scopes=[IndicatorScope.GLOBAL, IndicatorScope.REGION, IndicatorScope.BUS]
        ),
        "EPNS": IndicatorDefinition(
            code="EPNS",
            name="Expected Power Not Supplied",
            description="Potência esperada não suprida.",
            unit=IndicatorUnit.MW,
            category=IndicatorCategory.ADEQUACY,
            allowed_scopes=[IndicatorScope.GLOBAL, IndicatorScope.REGION, IndicatorScope.BUS]
        ),
        "EENS": IndicatorDefinition(
            code="EENS",
            name="Expected Energy Not Supplied",
            description="Energia esperada não suprida.",
            unit=IndicatorUnit.MWh_PER_YEAR,
            category=IndicatorCategory.ADEQUACY,
            allowed_scopes=[IndicatorScope.GLOBAL, IndicatorScope.REGION, IndicatorScope.BUS]
        ),
        "LOLF": IndicatorDefinition(
            code="LOLF",
            name="Loss of Load Frequency",
            description="Frequência de ocorrência de perda de carga.",
            unit=IndicatorUnit.OCCURRENCES_PER_YEAR,
            category=IndicatorCategory.ADEQUACY,
            allowed_scopes=[IndicatorScope.GLOBAL, IndicatorScope.REGION, IndicatorScope.BUS]
        ),
        "LOLD": IndicatorDefinition(
            code="LOLD",
            name="Loss of Load Duration",
            description="Duração média de uma ocorrência de perda de carga.",
            unit=IndicatorUnit.HOURS_PER_YEAR,
            category=IndicatorCategory.ADEQUACY,
            allowed_scopes=[IndicatorScope.GLOBAL, IndicatorScope.REGION, IndicatorScope.BUS]
        ),
        "LOLC": IndicatorDefinition(
            code="LOLC",
            name="Loss of Load Cost",
            description="Custo esperado associado à perda.",
            unit=IndicatorUnit.DOLLARS_PER_YEAR,
            category=IndicatorCategory.ECONOMIC,
            allowed_scopes=[IndicatorScope.GLOBAL, IndicatorScope.REGION, IndicatorScope.BUS]
        ),
        "UNAVAILABILITY": IndicatorDefinition(
            code="UNAVAILABILITY",
            name="Equipment Unavailability",
            description="Indisponibilidade forçada.",
            unit=IndicatorUnit.PERCENTAGE,
            category=IndicatorCategory.SECURITY,
            allowed_scopes=[IndicatorScope.GENERATOR, IndicatorScope.LINE, IndicatorScope.TRANSFORMER]
        )
    }

    @classmethod
    def validate_scope(cls, code: str, requested_scope: IndicatorScope) -> bool:
        """Lança erro se o motor tentar agregar um indicador em um escopo proibido."""
        indicator = cls.get(code)
        if requested_scope not in indicator.allowed_scopes:
            raise ValueError(f"Indicador {code} não suporta a análise em nível {requested_scope.value}")
        return True

    @classmethod
    def get(cls, code: str) -> IndicatorDefinition:
        code_upper = code.upper()
        if code_upper not in cls._CATALOG:
            raise ValueError(f"Indicador desconhecido: {code}")
        return cls._CATALOG[code_upper]