from enum import Enum

class TimeSeriesGranularity(str, Enum):
    HOURLY = "hourly"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"