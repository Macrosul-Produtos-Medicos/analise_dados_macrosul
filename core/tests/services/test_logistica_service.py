import pytest

from core.services.logistica_service import LogisticaService
from core.repositories.logistica_repository import LogisticaRepository

from core.services.exceptions import (
    DataNotFoundError,
    ServiceError,
    ValidationError,
    BusinessRuleError,
    DataNotFoundError,
    DataTransformationError,
)

from core.repositories.exceptions import (
    RepositoryError,
    ConnectionError as RepoConnectionError,
    QueryError as RepoQueryError,
)

@pytest.fixture
def logistica_service():
    return LogisticaService()

@pytest.mark.django_db
def test_logistica_service_instantiation(logistica_service):
    service = logistica_service
    assert service is not None
    assert isinstance(service, LogisticaService)
    assert service.repo is not None
    assert isinstance(service.repo, LogisticaRepository)


@pytest.fixture
def listar_transportadoras_mais_usadas_mock():
    """Raw data as it comes from the repository (before pivot)."""
    return [
        {
            "CardCode": "F00001",
            "CardName": "Transportadora A",
            "Total": 150,
            "Mes": 1,
            "Ano": 2024,
        },
        {
            "CardCode": "F00002",
            "CardName": "Transportadora B",
            "Total": 120,
            "Mes": 1,
            "Ano": 2024,
        },
        {
            "CardCode": "F00003",
            "CardName": "Transportadora C",
            "Total": 120,
            "Mes": 1,
            "Ano": 2025,
        },
        {
            "CardCode": "F00004",
            "CardName": "Transportadora D",
            "Total": 120,
            "Mes": 2,
            "Ano": 2025,
        },
    ]


@pytest.fixture
def listar_transportadoras_mais_usadas_expected():
    """Expected data after pivot transformation in service."""
    return [
        {"CardCode": "F00001", "CardName": "Transportadora A", "1-2024": 150, "1-2025": 0, "2-2025": 0},
        {"CardCode": "F00002", "CardName": "Transportadora B", "1-2024": 120, "1-2025": 0, "2-2025": 0},
        {"CardCode": "F00003", "CardName": "Transportadora C", "1-2024": 0, "1-2025": 120, "2-2025": 0},
        {"CardCode": "F00004", "CardName": "Transportadora D", "1-2024": 0, "1-2025": 0, "2-2025": 120},
    ]


@pytest.mark.django_db
def test_logistica_service_listar_transportadoras_mais_usadas(logistica_service, listar_transportadoras_mais_usadas_mock, listar_transportadoras_mais_usadas_expected):
    # Mock repository's cliente.fetch_all (raw data before pivot)
    logistica_service.repo.cliente.fetch_all = lambda sql, params=None: listar_transportadoras_mais_usadas_mock
    result, sql = logistica_service.listar_transportadoras_mais_usadas()
    
    # Result should be pivoted data
    assert result == listar_transportadoras_mais_usadas_expected
    assert isinstance(result, list)
    assert all(isinstance(item, dict) for item in result)
    assert sql is not None
    assert isinstance(sql, str)
    assert f"OFFSET 0 ROWS" in sql
    
@pytest.mark.django_db
def test_logistica_service_listar_transportadoras_mais_usadas_com_paginacao(logistica_service, listar_transportadoras_mais_usadas_mock, listar_transportadoras_mais_usadas_expected):
    # Mock repository's cliente.fetch_all (raw data before pivot)
    logistica_service.repo.cliente.fetch_all = lambda sql, params=None: listar_transportadoras_mais_usadas_mock
    offset = 2
    fetch_next = 2
    result, sql = logistica_service.listar_transportadoras_mais_usadas(offset=offset, fetch_next=fetch_next)
    
    # Result should be pivoted data
    assert result == listar_transportadoras_mais_usadas_expected
    assert isinstance(result, list)
    assert all(isinstance(item, dict) for item in result)
    assert sql is not None
    assert isinstance(sql, str)
    assert f"OFFSET {offset} ROWS" in sql
    assert f"FETCH NEXT {fetch_next} ROWS ONLY" in sql
    
@pytest.mark.django_db
def test_logistica_service_listar_transportadoras_mais_usadas_invalid_pagination(logistica_service):
    expected_exception = ValidationError
    with pytest.raises(expected_exception):
        logistica_service.listar_transportadoras_mais_usadas(offset=-1, fetch_next=10)
    with pytest.raises(expected_exception):
        logistica_service.listar_transportadoras_mais_usadas(offset=0, fetch_next=-5)
        
@pytest.mark.django_db
def test_logistica_service_listar_transportadoras_mais_usadas_zero_fetch_next(logistica_service):
    expected_exception = ValidationError
    with pytest.raises(expected_exception):
        logistica_service.listar_transportadoras_mais_usadas(offset=0, fetch_next=0)
        
@pytest.mark.django_db
@pytest.mark.parametrize("repository_exception, expected_exception, error_message", [
    (RepoConnectionError, ServiceError, "Erro de conexão com o banco de dados"),
    (RepoQueryError, ServiceError, "Erro ao executar consulta"),
    (RepositoryError, ServiceError, "Erro no repositório"),
    (Exception, ServiceError, "Erro inesperado no serviço"),
])
def test_listar_transportadoras_mais_usadas_handling_repository_exceptions(
    logistica_service,
    repository_exception,
    expected_exception,
    error_message
):
    def raise_exception(*args, **kwargs):
        raise repository_exception("Simulated repository error")
    
    # Mock the repository method directly (not cliente.fetch_all)
    # This way the service decorator receives the exception directly
    logistica_service.repo.listar_transportadoras_mais_usadas = raise_exception
    
    with pytest.raises(expected_exception) as exc_info:
        logistica_service.listar_transportadoras_mais_usadas()
    
    assert error_message in str(exc_info.value)
    
@pytest.mark.django_db
def test_listar_transportadoras_mais_usadas_result(logistica_service, listar_transportadoras_mais_usadas_mock):
    # Mock service method and but don't mock sql generation
    logistica_service.repo.cliente.fetch_all = lambda sql, params=None: listar_transportadoras_mais_usadas_mock
    result, sql = logistica_service.listar_transportadoras_mais_usadas()
    
    # result should be a pivot table (dict) with Mes_Ano as column (underscore separator)
    # Check that the result contains expected columns
    
    expected_columns = {"CardCode", "CardName", "1-2024", "1-2025", "2-2025"}
    result_columns = set(result[0].keys())
    assert expected_columns == result_columns
    
@pytest.mark.django_db
def test_logistica_service_listar_transportadoras_mais_usadas_empty_result(logistica_service):
    # Mock repository's cliente.fetch_all to return empty list
    logistica_service.repo.cliente.fetch_all = lambda sql, params=None: []
    
    with pytest.raises(DataNotFoundError):
        result, sql = logistica_service.listar_transportadoras_mais_usadas()
        
@pytest.mark.django_db
@pytest.mark.parametrize("exception, expected_exception, error_message", [
    (KeyError("SomeKey"), DataTransformationError, "Campo não encontrado nos dados"),
    (TypeError("SomeTypeError"), DataTransformationError, "Tipo de dado inválido"),
    (ZeroDivisionError("division by zero"), DataTransformationError, "Erro de cálculo (divisão por zero)"),
])
def test_logistica_service_listar_transportadoras_mais_usadas_data_transformation_error(
    logistica_service, 
    listar_transportadoras_mais_usadas_mock,
    exception,
    expected_exception,
    error_message
):
    # Mock repository's cliente.fetch_all to return valid data
    logistica_service.repo.cliente.fetch_all = lambda sql, params=None: listar_transportadoras_mais_usadas_mock
    
    # Patch the pivot_table method to raise the desired exception
    original_pivot_table = logistica_service.pivot_table
    
    def raise_exception(*args, **kwargs):
        raise exception
    
    logistica_service.pivot_table = raise_exception
    
    with pytest.raises(expected_exception) as exc_info:
        logistica_service.listar_transportadoras_mais_usadas()
    
    assert error_message in str(exc_info.value)
    
    # Restore original method
    logistica_service.pivot_table = original_pivot_table
    


    
    
    