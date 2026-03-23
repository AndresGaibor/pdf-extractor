class DomainError(Exception):
    """Base class for domain errors"""
    pass

class PDFProcessingError(DomainError):
    """Error raised when PDF processing fails"""
    pass

class ExcelGenerationError(DomainError):
    """Error raised when Excel generation fails"""
    pass

class ExtractionError(DomainError):
    """Error raised when data extraction fails for a specific paragraph"""
    pass
