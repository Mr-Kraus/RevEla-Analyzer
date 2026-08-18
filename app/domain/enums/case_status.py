from enum import Enum

class CaseStatus(str, Enum):
    DISCOVERED = "DISCOVERED" # [cite: 398]
    VALIDATING = "VALIDATING" # [cite: 399]
    INGESTING = "INGESTING"   # [cite: 400]
    READY = "READY"           # [cite: 401]
    PARTIAL = "PARTIAL"       # [cite: 402]
    FAILED = "FAILED"         # [cite: 403]
    ARCHIVED = "ARCHIVED"     # [cite: 404]