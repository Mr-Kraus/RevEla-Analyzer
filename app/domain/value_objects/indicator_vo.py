from enum import Enum

class IndicatorScope(Enum):
    GLOBAL = "GLOBAL"
    REGION = "REGION"
    BUS = "BUS"
    GENERATOR = "GENERATOR"
    LINE = "LINE"
    TRANSFORMER = "TRANSFORMER"

class IndicatorUnit(Enum):
    HOURS_PER_YEAR = "h/ano"
    OCCURRENCES_PER_YEAR = "occ/ano"
    MW = "MW"
    MWh_PER_YEAR = "MWh/ano"
    DOLLARS_PER_YEAR = "$/ano"
    PERCENTAGE = "%"
    DIMENSIONLESS = "-"

class IndicatorCategory(Enum):
    ADEQUACY = "Adequacy"
    SECURITY = "Security"
    ECONOMIC = "Economic"