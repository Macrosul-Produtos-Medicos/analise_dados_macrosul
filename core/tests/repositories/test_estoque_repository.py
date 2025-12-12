import pyodbc
import pytest

from core.repositories.estoque_repository import EstoqueRepository
from core.repositories.exceptions import ConnectionError, QueryError, RepositoryError

@pytest.fixture
def estoque_repository():
    return EstoqueRepository()

@pytest.fixture
def listar_hits_mock():
    return [
        {
            "ItemCode": "A0001",
            "ItemName": "Produto A",
            "CardCode": "F00001",
            "Hits12Meses": 150,
            "Hits30Dias": 20,
            "Pedidos06Meses": 6,
            "Vendas06Meses": 6
        },
        {
            "ItemCode": "B0002",
            "ItemName": "Produto B",
            "CardCode": "F00001",
            "Hits12Meses": 150,
            "Hits30Dias": 20,
            "Pedidos06Meses": 6,
            "Vendas06Meses": 6
        },
        {
            "ItemCode": "C0003",
            "ItemName": "Produto C",
            "CardCode": "F00002",
            "Hits12Meses": 150,
            "Hits30Dias": 20,
            "Pedidos06Meses": 3,
            "Vendas06Meses": 6
        },
        {
            "ItemCode": "C0004",
            "ItemName": "Produto D",
            "CardCode": "F00003",
            "Hits12Meses": 150,
            "Hits30Dias": 20,
            "Pedidos06Meses": 6,
            "Vendas06Meses": 6
        },
    ]

@pytest.mark.django_db
def test_estoque_repository_instantiation(estoque_repository):
    repo = estoque_repository
    assert repo is not None
    assert isinstance(repo, EstoqueRepository)
    assert repo.cliente is not None

@pytest.mark.django_db
def test_listar_hits(estoque_repository, listar_hits_mock):
    # Mock the cliente's fetch_all method
    estoque_repository.cliente.fetch_all = lambda sql, params=None: listar_hits_mock
    result, sql = estoque_repository.listar_hits()
    assert result == listar_hits_mock
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
def test_listar_hits_query_error(estoque_repository, exception, expected_exception):
    def raise_exception(sql, params=None):
        raise exception("Test exception")

    estoque_repository.cliente.fetch_all = raise_exception

    with pytest.raises(expected_exception):
        estoque_repository.listar_hits()

@pytest.fixture
def listar_pedidos_em_transito_mock():
    return [
        {
            "ItemCode": 1001,
            "ItemName": "C0001",
            "INVQTY_Mensal": "150",
            "AnoMes": "2025-01",
        },
        {
            "ItemCode": 1002,
            "ItemName": "C0002",
            "INVQTY_Mensal": "150",
            "AnoMes": "2025-01",
        },
        {
            "ItemCode": 1002,
            "ItemName": "C0002",
            "INVQTY_Mensal": "150",
            "AnoMes": "2025-05",
        },
        {
            "ItemCode": 1003,
            "ItemName": "C0003",
            "INVQTY_Mensal": "150",
            "AnoMes": "2025-01",
        },
    ]

@pytest.mark.django_db
def test_listar_pedidos_em_transito(estoque_repository, listar_pedidos_em_transito_mock):
    # Mock the cliente's fetch_all method
    estoque_repository.cliente.fetch_all = lambda sql, params=None: listar_pedidos_em_transito_mock
    result, sql = estoque_repository.listar_pedidos_em_transito()
    assert result == listar_pedidos_em_transito_mock
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
def test_listar_pedidos_em_transito_query_error(estoque_repository, exception, expected_exception):
    def raise_exception(sql, params=None):
        raise exception("Test exception")

    estoque_repository.cliente.fetch_all = raise_exception

    with pytest.raises(expected_exception):
        estoque_repository.listar_pedidos_em_transito()

@pytest.fixture
def listar_pedidos_de_venda_mock():
    return [
        {
            "ItemCode": "A0001",
            "ItemName": "Produto A",
            "CardCode": "F00001",
            "QuantidadeVendida": 50,
            "AnoMes": "2025-01",
        },
        {
            "ItemCode": "B0002",
            "ItemName": "Produto B",
            "CardCode": "F00001",
            "QuantidadeVendida": 30,
            "AnoMes": "2025-02",
        },
        {
            "ItemCode": "C0003",
            "ItemName": "Produto C",
            "CardCode": "F00002",
            "QuantidadeVendida": 20,
            "AnoMes": "2025-03",
        },
        {
            "ItemCode": "D0004",
            "ItemName": "Produto D",
            "CardCode": "F00003",
            "QuantidadeVendida": 10,
            "AnoMes": "2025-02",
        },
    ]       

@pytest.mark.django_db
def test_listar_pedidos_de_venda(estoque_repository, listar_pedidos_de_venda_mock):
    # Mock the cliente's fetch_all method
    data_inicio = "2025-01-01"
    data_fim = "2025-02-28"
    estoque_repository.cliente.fetch_all = lambda sql, params=None: listar_pedidos_de_venda_mock
    result, sql = estoque_repository.listar_pedidos_de_venda(data_inicio, data_fim)
    assert result == listar_pedidos_de_venda_mock
    assert isinstance(result, list)
    assert all(isinstance(item, dict) for item in result)
    assert sql is not None
    assert isinstance(sql, str)
    
@pytest.mark.django_db
def test_listar_pedidos_de_venda_check_sql(estoque_repository, listar_pedidos_de_venda_mock):
    # Mock the cliente's fetch_all method
    data_inicio = "2025-01-01"
    data_fim = "2025-02-28"
    estoque_repository.cliente.fetch_all = lambda sql, params=None: listar_pedidos_de_venda_mock
    result, sql = estoque_repository.listar_pedidos_de_venda(data_inicio, data_fim)
    assert f"DECLARE @DataFim DATE = '{data_fim}';" in sql
    assert f"DECLARE @DataInicio DATE = '{data_inicio}';" in sql  # Since we use GETDATE() in the query
    assert f"OINV.DocDate BETWEEN @DataInicio AND @DataFim" in sql

@pytest.mark.django_db
@pytest.mark.parametrize("exception, expected_exception", [
    (pyodbc.InterfaceError, ConnectionError),
    (pyodbc.OperationalError, ConnectionError),
    (pyodbc.ProgrammingError, QueryError),
    (pyodbc.DataError, QueryError),
    (pyodbc.DatabaseError, RepositoryError),
    (Exception, RepositoryError),
])
def test_listar_pedidos_de_venda_query_error(estoque_repository, exception, expected_exception):
    def raise_exception(sql, params=None):
        raise exception("Test exception")

    estoque_repository.cliente.fetch_all = raise_exception

    with pytest.raises(expected_exception):
        estoque_repository.listar_pedidos_de_venda("2025-01-01", "2025-02-28")
        
@pytest.mark.django_db
def test_listar_pedidos_de_venda_date_none(estoque_repository):
    estoque_repository.cliente.fetch_all = lambda sql, params=None: listar_pedidos_de_venda_mock
    result, sql = estoque_repository.listar_pedidos_de_venda()
    assert f"DECLARE @DataFim DATE = GETDATE();" in sql
    assert f"DECLARE @DataInicio DATE = DATEADD(MONTH, -6, DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()), 0))" in sql  
    assert f"OINV.DocDate BETWEEN @DataInicio AND @DataFim" in sql in sql

@pytest.mark.django_db
def test_listar_pedidos_de_venda_date_partial(estoque_repository):
    estoque_repository.cliente.fetch_all = lambda sql, params=None: listar_pedidos_de_venda_mock
    result, sql = estoque_repository.listar_pedidos_de_venda(data_inicio="2025-01-01")
    assert f"DECLARE @DataFim DATE = GETDATE();" in sql
    assert f"DECLARE @DataInicio DATE = '2025-01-01';" in sql  
    assert f"OINV.DocDate BETWEEN @DataInicio AND @DataFim" in sql in sql
    
@pytest.mark.django_db
def test_listar_pedidos_de_venda_date_partial_end(estoque_repository):
    estoque_repository.cliente.fetch_all = lambda sql, params=None: listar_pedidos_de_venda_mock
    result, sql = estoque_repository.listar_pedidos_de_venda(data_fim="2025-06-30")
    assert f"DECLARE @DataFim DATE = '2025-06-30';" in sql
    assert f"DECLARE @DataInicio DATE = DATEADD(MONTH, -6, DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()), 0))" in sql  
    assert f"OINV.DocDate BETWEEN @DataInicio AND @DataFim" in sql in sql

@pytest.mark.django_db
def test_listar_pedidos_de_venda_invalid_date(estoque_repository):
    with pytest.raises(QueryError):
        estoque_repository.listar_pedidos_de_venda(data_inicio="invalid-date", data_fim="2025-06-30")

@pytest.mark.django_db
@pytest.mark.parametrize("data_inicio, data_fim", [
    ("2025-06-30", "2025-01-01"),
    ("2025-12-31", "2025-01-01"),
])
def test_listar_pedidos_de_venda_invalid_range(estoque_repository, data_inicio, data_fim):
    with pytest.raises(QueryError):
        estoque_repository.listar_pedidos_de_venda(data_inicio=data_inicio, data_fim=data_fim)

@pytest.fixture
def listar_saida_de_produtos_mock():
    return [
        {
            "ItemCode": "A0001",
            "ItemName": "Produto A",
            "CardCode": "F00001",
            "CardName": "Fornecedor A",
            "QuantidadeSaida": 100,
            "AnoMes": "2025-01",
        },
        {
            "ItemCode": "B0002",
            "ItemName": "Produto B",
            "CardCode": "F00001",
            "CardName": "Fornecedor A",
            "QuantidadeSaida": 80,
            "AnoMes": "2025-02",
        },
        {
            "ItemCode": "C0003",
            "ItemName": "Produto C",
            "CardCode": "F00002",
            "CardName": "Fornecedor B",
            "QuantidadeSaida": 60,
            "AnoMes": "2025-03",
        },
        {
            "ItemCode": "D0004",
            "ItemName": "Produto D",
            "CardCode": "F00003",
            "CardName": "Fornecedor C",
            "QuantidadeSaida": 40,
            "AnoMes": "2025-02",
        },
    ]

@pytest.mark.django_db
def test_listar_saida_de_produtos(estoque_repository, listar_saida_de_produtos_mock):
    # Mock the cliente's fetch_all method
    estoque_repository.cliente.fetch_all = lambda sql, params=None: listar_saida_de_produtos_mock
    result, sql = estoque_repository.listar_saida_de_produtos('2025-01-01', '2025-06-30')
    assert result == listar_saida_de_produtos_mock
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
def test_listar_saida_de_produtos_query_error(estoque_repository, exception, expected_exception):
    def raise_exception(sql, params=None):
        raise exception("Test exception")

    estoque_repository.cliente.fetch_all = raise_exception

    with pytest.raises(expected_exception):
        estoque_repository.listar_saida_de_produtos('2025-01-01', '2025-06-30')
        
@pytest.mark.django_db
def test_listar_saida_de_produtos_date_none(estoque_repository):
    estoque_repository.cliente.fetch_all = lambda sql, params=None: listar_saida_de_produtos_mock
    result, sql = estoque_repository.listar_saida_de_produtos()
    assert f"@DataInicio DATE = DATEADD(MONTH, -6, GETDATE());" in sql
    assert f"@DataFim DATE = GETDATE();" in sql
    
@pytest.mark.django_db
def test_listar_saida_de_produtos_date_partial(estoque_repository):
    estoque_repository.cliente.fetch_all = lambda sql, params=None: listar_saida_de_produtos_mock
    result, sql = estoque_repository.listar_saida_de_produtos(data_inicio="2025-01-01")
    assert f"@DataInicio DATE = '2025-01-01';" in sql
    assert f"@DataFim DATE = GETDATE();" in sql

@pytest.mark.django_db
def test_listar_saida_de_produtos_date_partial_end(estoque_repository):
    estoque_repository.cliente.fetch_all = lambda sql, params=None: listar_saida_de_produtos_mock
    result, sql = estoque_repository.listar_saida_de_produtos(data_fim="2025-06-30")
    assert f"@DataInicio DATE = DATEADD(MONTH, -6, GETDATE());" in sql
    assert f"@DataFim DATE = '2025-06-30';" in sql
    
@pytest.mark.django_db
def test_listar_saida_de_produtos_invalid_date(estoque_repository):
    with pytest.raises(QueryError):
        estoque_repository.listar_saida_de_produtos(data_inicio="invalid-date", data_fim="2025-06-30")
        
@pytest.mark.django_db
@pytest.mark.parametrize("data_inicio, data_fim", [
    ("2025-06-30", "2025-01-01"),
    ("2025-12-31", "2025-01-01"),
])
def test_listar_saida_de_produtos_invalid_range(estoque_repository, data_inicio, data_fim):
    with pytest.raises(QueryError):
        estoque_repository.listar_saida_de_produtos(data_inicio=data_inicio, data_fim=data_fim)

