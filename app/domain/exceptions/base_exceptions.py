class RevelaAnalyzerError(Exception):
    """Exceção base para toda a aplicação."""
    pass

class CaseNotFoundError(RevelaAnalyzerError): # [cite: 548]
    pass

class InvalidCaseStructureError(RevelaAnalyzerError): # [cite: 549]
    pass

class UnreadableSourceFileError(RevelaAnalyzerError): # [cite: 550]
    pass

class UnsupportedDatasetError(RevelaAnalyzerError): # [cite: 551]
    pass

class ValidationError(RevelaAnalyzerError): # [cite: 552]
    pass

class IngestionError(RevelaAnalyzerError): # [cite: 553]
    pass

class RepositoryError(RevelaAnalyzerError): # [cite: 554]
    pass