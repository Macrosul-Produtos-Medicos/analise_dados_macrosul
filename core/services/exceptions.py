# core/services/exceptions.py

class ServiceError(Exception):
    """Base exception for service layer."""
    pass


class ValidationError(ServiceError):
    """Invalid input parameters."""
    pass


class BusinessRuleError(ServiceError):
    """Business rule violation."""
    pass


class DataNotFoundError(ServiceError):
    """Expected data was not found."""
    pass

class DataTransformationError(ServiceError):
    "Error while transforming/processing data."
    pass
