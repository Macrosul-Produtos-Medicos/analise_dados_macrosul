import pytest
import pyodbc

from core.repositories.financeiro_repository import FinanceiroRepository
from core.repositories.exceptions import ConnectionError, QueryError, RepositoryError

@pytest.fixture
def financeiro_repository():
    return FinanceiroRepository()

@pytest.mark.django_db
def test_financeiro_repository_instantiation():
    repo = FinanceiroRepository()
    assert repo is not None
    assert isinstance(repo, FinanceiroRepository)
    assert repo.cliente is not None


@pytest.fixture
def listar_rentabilidade_itens_response():
    return [
        {
            "ItemCode": "I00001",
            "ItemName": "Item A",
            "TipoDoNegocio": "B2B",
            "Quantidade": 125,
            "PrecoMinimoUnitario": 90.0,
            "FaturamentoPorItem": 8961.78,
            "Rentabilidade": -0.29
        },
        {
            "ItemCode": "I00002",
            "ItemName": "Item B",
            "TipoDoNegocio": "B2B",
            "Quantidade": 100,
            "PrecoMinimoUnitario": 80.0,
            "FaturamentoPorItem": 8000.0,
            "Rentabilidade": 0.20
        },
        {
            "ItemCode": "I00003",
            "ItemName": "Item C",
            "TipoDoNegocio": "B2C",
            "Quantidade": 50,
            "PrecoMinimoUnitario": 150.0,
            "FaturamentoPorItem": 7500.0,
            "Rentabilidade": 0.35
        }
    ]


@pytest.mark.django_db
def test_listar_rentabilidade_itens(financeiro_repository, listar_rentabilidade_itens_response):
    
    financeiro_repository.cliente.fetch_all = lambda sql, params = None: listar_rentabilidade_itens_response
    result, sql = financeiro_repository.listar_rentabilidade_itens()
    assert result == listar_rentabilidade_itens_response
    assert isinstance(result, list)
    assert all(isinstance(item, dict) for item in result)
    assert sql is not None
    assert "DECLARE @DataFim DATE = GETDATE()" in sql
    assert "DECLARE @DataInicio DATE = DATEADD(MONTH, -12, GETDATE())" in sql

@pytest.mark.django_db
def test_listar_rentabilidade_date_range(financeiro_repository):
    data_inicio = "2023-01-01"
    data_fim = "2023-12-31"
    
    financeiro_repository.cliente.fetch_all = lambda sql, params = None: []
    result, sql = financeiro_repository.listar_rentabilidade_itens(data_inicio, data_fim)
    assert f"@DataInicio DATE = '{data_inicio}'" in sql
    assert f"@DataFim DATE = '{data_fim}'" in sql
    
@pytest.mark.django_db
@pytest.mark.parametrize("exception, expected_exception", [
    (pyodbc.InterfaceError, ConnectionError),
    (pyodbc.OperationalError, ConnectionError),
    (pyodbc.ProgrammingError, QueryError),
    (pyodbc.DataError, QueryError),
    (pyodbc.DatabaseError, RepositoryError),
    (Exception, RepositoryError),
])
def test_listar_rentabilidade_itens_exceptions(financeiro_repository, exception, expected_exception):
    def raise_exception(sql, params=None):
        raise exception("Test exception")
    
    financeiro_repository.cliente.fetch_all = raise_exception
    
    with pytest.raises(expected_exception):
        financeiro_repository.listar_rentabilidade_itens()
        
@pytest.mark.django_db
def test_listar_rentabilidade_itens_default_dates(financeiro_repository):
    
    data_inicio = '2025-06-01'
    
    financeiro_repository.cliente.fetch_all = lambda sql, params = None: []
    result, sql = financeiro_repository.listar_rentabilidade_itens(data_inicio=data_inicio)
    assert f"@DataInicio DATE = '{data_inicio}'" in sql
    assert f"@DataFim DATE = GETDATE()" in sql
    
@pytest.mark.django_db
def test_listar_rentabilidade_itens_only_data_fim(financeiro_repository):
    data_fim = '2025-12-31'
    
    financeiro_repository.cliente.fetch_all = lambda sql, params = None: []
    result, sql = financeiro_repository.listar_rentabilidade_itens(data_fim=data_fim)
    assert f"@DataInicio DATE = DATEADD(MONTH, -12, GETDATE())" in sql
    assert f"@DataFim DATE = '{data_fim}'" in sql
    
@pytest.mark.django_db
def test_listar_rentabilidade_itens_invalid_date_format(financeiro_repository):
    invalid_date = "31-12-2023"
    
    financeiro_repository.cliente.fetch_all = lambda sql, params = None: []
    
    with pytest.raises(RepositoryError):
        financeiro_repository.listar_rentabilidade_itens(data_inicio=invalid_date)
        
@pytest.mark.django_db
def test_listar_rentabilidade_itens_invalid_range(financeiro_repository):
    data_inicio = "2023-12-31"
    data_fim = "2023-01-01"
    
    financeiro_repository.cliente.fetch_all = lambda sql, params = None: []
    
    with pytest.raises(RepositoryError):
        financeiro_repository.listar_rentabilidade_itens(data_inicio=data_inicio, data_fim=data_fim)