import functools

from core.repositories.exceptions import (
    RepositoryError,
    ConnectionError as RepoConnectionError,
    QueryError as RepoQueryError,
)
from .exceptions import (
    ServiceError,
    ValidationError,
    BusinessRuleError,
    DataNotFoundError,
    DataTransformationError,
)


def handle_service_errors(func):
    """
    Decorator that handles exceptions in the service layer and transforms them
    into user-friendly exceptions for the view layer.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        
        # Repository errors (bubbled up from repository layer)
        except RepoConnectionError as e:
            raise ServiceError(f"Erro de conexão com o banco de dados: {e}") from e
        
        except RepoQueryError as e:
            raise ServiceError(f"Erro ao executar consulta: {e}") from e
        
        except RepositoryError as e:
            raise ServiceError(f"Erro no repositório: {e}") from e
        
        # Data transformation errors
        except KeyError as e:
            raise DataTransformationError(f"Campo não encontrado nos dados: {e}") from e
        
        except TypeError as e:
            raise DataTransformationError(f"Tipo de dado inválido: {e}") from e
        
        except ZeroDivisionError as e:
            raise DataTransformationError(f"Erro de cálculo (divisão por zero): {e}") from e
        
        # Validation errors (let them pass through as-is)
        except ValidationError:
            raise
        
        except BusinessRuleError:
            raise
        
        except DataNotFoundError:
            raise
        
        # Service errors (let them pass through as-is)
        except ServiceError:
            raise
        
        # Unexpected errors
        except Exception as e:
            raise ServiceError(f"Erro inesperado no serviço: {e}") from e
    
    return wrapper


def validate_pagination(func):
    """
    Decorator that validates pagination parameters (offset, fetch_next, page, page_size).
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Check offset
        offset = kwargs.get('offset')
        if offset is not None and offset < 0:
            raise ValidationError("offset não pode ser negativo")
        
        # Check fetch_next
        fetch_next = kwargs.get('fetch_next')
        if fetch_next is not None and fetch_next <= 0:
            raise ValidationError("fetch_next deve ser maior que zero")
        
        # Check page
        page = kwargs.get('page')
        if page is not None and page < 1:
            raise ValidationError("page deve ser maior ou igual a 1")
        
        # Check page_size
        page_size = kwargs.get('page_size')
        if page_size is not None and page_size <= 0:
            raise ValidationError("page_size deve ser maior que zero")
        
        return func(*args, **kwargs)
    
    return wrapper
