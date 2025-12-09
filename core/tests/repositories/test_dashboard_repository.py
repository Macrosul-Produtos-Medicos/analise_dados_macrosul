import pytest
import pyodbc

from core.repositories.dashboard_repository import DashboardRepository
from core.repositories.exceptions import ConnectionError, QueryError, RepositoryError


@pytest.fixture
def dashboard_repository():
    return DashboardRepository()

@pytest.fixture
def listar_notas_fiscais_mock():
    return [
        {
            "quantidade_notas": 100,
            "quantidade_itens": 250,
            "data_emissao": "2023-01-15",
            "mes_emissao": 1,
            "semana_emissao": 3,
            "ano_emissao": 2023
        },
        {
            "quantidade_notas": 42,
            "quantidade_itens": 242,
            "data_emissao": "2024-01-16",
            "mes_emissao": 1,
            "semana_emissao": 3,
            "ano_emissao": 2024
        }
    ]


@pytest.mark.django_db
def test_dashboard_repository_instantiation():
    repo = DashboardRepository()
    assert repo is not None
    assert isinstance(repo, DashboardRepository)
    assert repo.cliente is not None
    
@pytest.mark.django_db
def test_listar_notas_fiscais_method(dashboard_repository, listar_notas_fiscais_mock):
    
    # Mock the cliente's fetch_all method
    dashboard_repository.cliente.fetch_all = lambda sql, params=None: listar_notas_fiscais_mock
    result, sql = dashboard_repository.listar_notas_fiscais()
    assert result == listar_notas_fiscais_mock
    assert isinstance(result, list)
    assert all(isinstance(item, dict) for item in result)

@pytest.mark.django_db
def test_listar_notas_fiscais_empty_result(dashboard_repository):
    # Mock the cliente's fetch_all method to return an empty list
    dashboard_repository.cliente.fetch_all = lambda sql, params=None: []
    result, sql = dashboard_repository.listar_notas_fiscais()
    assert result == []
    assert isinstance(result, list)
    assert len(result) == 0
    assert isinstance(sql, str)
    
@pytest.mark.django_db
def test_listar_notas_fiscais_handling_errors(dashboard_repository):
    # Mock the cliente's fetch_all method to raise an exception
    def mock_fetch_all(sql):
        raise Exception("Database error")
    
    dashboard_repository.cliente.fetch_all = mock_fetch_all
    
    with pytest.raises(Exception) as excinfo:
        dashboard_repository.listar_notas_fiscais()
        
@pytest.mark.django_db
def test_listar_notas_fiscais_with_year_filter(dashboard_repository, listar_notas_fiscais_mock):
    # Mock the cliente's fetch_all method, filter results by year
    def mock_fetch_all(sql, params=None):
        return [item for item in listar_notas_fiscais_mock if item["ano_emissao"] == 2023]
    
    dashboard_repository.cliente.fetch_all = mock_fetch_all
    result, sql = dashboard_repository.listar_notas_fiscais(ano=2023)
    assert all(item["ano_emissao"] == 2023 for item in result)
    assert len(result) == 1
    assert result[0]["quantidade_notas"] == 100
    assert sql is not None
    assert isinstance(sql, str)
    assert 'AND YEAR(OINV.DocDate) = ?' in sql or 'AND OINV.DocDate' in sql
    

@pytest.mark.django_db
def test_listar_notas_fiscais_sql_integrity(dashboard_repository):
    # Mock the cliente's fetch_all method to return an empty list
    dashboard_repository.cliente.fetch_all = lambda sql, params=None: []
    result, sql = dashboard_repository.listar_notas_fiscais()
    expected_sql_start = """
            SELECT
                COUNT(distinct(OINV.Serial)) AS quantidade_notas,
                ,CAST(SUM(INV1.Quantity) AS int) as quantidade_itens,
                ,OINV.DocDate as data_emissao
                ,DATEPART(MONTH, OINV.DocDate) as mes_emissao
                ,DATEPART(WEEK, OINV.DocDate) as semana_emissao
                ,DATEPART(YEAR, OINV.DocDate) as ano_emissao
            FROM OINV OINV
            JOIN INV1 INV1 ON OINV.DocEntry = INV1.DocEntry
            WHERE 
                OINV.CANCELED = 'N'
                AND OINV.InvntSttus = 'O'
            GROUP BY
                OINV.DocDate
            ORDER BY
                OINV.DocDate
        """
    assert sql.strip().startswith(expected_sql_start.strip())

@pytest.mark.django_db
@pytest.mark.parametrize("exception, expected_exception", [
    (pyodbc.InterfaceError, ConnectionError),
    (pyodbc.OperationalError, ConnectionError),
    (pyodbc.ProgrammingError, QueryError),
    (pyodbc.DataError, QueryError),
    (pyodbc.DatabaseError, RepositoryError),
    (Exception, RepositoryError),
])
def test_listar_notas_fiscais_handling_errors_specific(dashboard_repository, exception, expected_exception):
    # Mock the cliente's fetch_all method to raise the specified exception
    def mock_fetch_all(sql, params=None):
        raise exception
    
    dashboard_repository.cliente.fetch_all = mock_fetch_all
    
    with pytest.raises(expected_exception) as excinfo:
        dashboard_repository.listar_notas_fiscais()
        
