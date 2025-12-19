import pytest
import pyodbc

from core.repositories.logistica_repository import LogisticaRepository
from core.repositories.exceptions import ConnectionError, QueryError, RepositoryError

@pytest.fixture
def logistica_repository():
    return LogisticaRepository()

@pytest.fixture
def listar_transportadoras_mais_usadas_mock():
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

@pytest.mark.django_db
def test_logistica_repository_instantiation(logistica_repository):
    repo = logistica_repository
    assert repo is not None
    assert isinstance(repo, LogisticaRepository)
    assert repo.cliente is not None
    
@pytest.mark.django_db
def test_listar_transportadoras_mais_usadas(logistica_repository, listar_transportadoras_mais_usadas_mock):
    # Mock the cliente's fetch_all method
    logistica_repository.cliente.fetch_all = lambda sql, params=None: listar_transportadoras_mais_usadas_mock
    result, sql = logistica_repository.listar_transportadoras_mais_usadas()
    assert result == listar_transportadoras_mais_usadas_mock
    assert isinstance(result, list)
    assert all(isinstance(item, dict) for item in result)
    assert sql is not None
    assert isinstance(sql, str)
    
@pytest.mark.django_db
@pytest.mark.parametrize("exception, expected_exception", [
    (pyodbc.InterfaceError, ConnectionError),
    (pyodbc.OperationalError, ConnectionError),
    (pyodbc.ProgrammingError, QueryError),
    (pyodbc.DataError, QueryError),
    (pyodbc.DatabaseError, RepositoryError),
    (Exception, RepositoryError),
])
def test_listar_transportadoras_mais_usadas_exceptions(logistica_repository, exception, expected_exception):
    def raise_exception(sql, params=None):
        raise exception("Simulated database error")
    
    # Mock the cliente's fetch_all method to raise the specified exception
    logistica_repository.cliente.fetch_all = raise_exception
    
    with pytest.raises(expected_exception):
        logistica_repository.listar_transportadoras_mais_usadas()
        
@pytest.mark.django_db
def test_listar_transportadoras_mais_usadas_primeiros_registros(logistica_repository, listar_transportadoras_mais_usadas_mock):
    # Mock the cliente's fetch_all method
    logistica_repository.cliente.fetch_all = lambda sql, params=None: listar_transportadoras_mais_usadas_mock
    result, sql = logistica_repository.listar_transportadoras_mais_usadas(offset=0, fetch_next=2)
    assert 'OFFSET 0 ROWS' in sql
    assert 'FETCH NEXT 2 ROWS ONLY' in sql
    
@pytest.mark.django_db
def test_listar_transportadoras_mais_usadas_offset_e_fetch(logistica_repository, listar_transportadoras_mais_usadas_mock):
    # Mock the cliente's fetch_all method
    logistica_repository.cliente.fetch_all = lambda sql, params=None: listar_transportadoras_mais_usadas_mock
    offset = 2
    fetch_next = 2
    result, sql = logistica_repository.listar_transportadoras_mais_usadas(offset=offset, fetch_next=fetch_next)
    assert f'OFFSET {offset} ROWS' in sql
    assert f'FETCH NEXT {fetch_next} ROWS ONLY' in sql
    
@pytest.mark.django_db
def test_listar_transportadoras_mais_usadas_sem_fetch_next(logistica_repository, listar_transportadoras_mais_usadas_mock):
    # Mock the cliente's fetch_all method
    logistica_repository.cliente.fetch_all = lambda sql, params=None: listar_transportadoras_mais_usadas_mock
    offset = 5
    result, sql = logistica_repository.listar_transportadoras_mais_usadas(offset=offset, fetch_next=None)
    assert f'OFFSET {offset} ROWS' in sql
    assert 'FETCH NEXT' not in sql


# ===================== Testes contar_transportadoras =====================

@pytest.mark.django_db
def test_contar_transportadoras(logistica_repository):
    """Test counting unique carriers."""
    logistica_repository.cliente.fetch_one = lambda sql, params=None: {"Total": 42}
    result, sql = logistica_repository.contar_transportadoras()
    
    assert result == 42
    assert isinstance(sql, str)
    assert 'COUNT(DISTINCT' in sql
    assert 'CardCode' in sql


@pytest.mark.django_db
def test_contar_transportadoras_empty_result(logistica_repository):
    """Test counting when no carriers found."""
    logistica_repository.cliente.fetch_one = lambda sql, params=None: None
    result, sql = logistica_repository.contar_transportadoras()
    
    assert result == 0


@pytest.mark.django_db
@pytest.mark.parametrize("exception, expected_exception", [
    (pyodbc.InterfaceError, ConnectionError),
    (pyodbc.OperationalError, ConnectionError),
    (pyodbc.ProgrammingError, QueryError),
    (pyodbc.DatabaseError, RepositoryError),
    (Exception, RepositoryError),
])
def test_contar_transportadoras_exceptions(logistica_repository, exception, expected_exception):
    """Test exception handling for contar_transportadoras."""
    def raise_exception(sql, params=None):
        raise exception("Simulated database error")
    
    logistica_repository.cliente.fetch_one = raise_exception
    
    with pytest.raises(expected_exception):
        logistica_repository.contar_transportadoras()