import pytest
from unittest.mock import patch, MagicMock
from core.services.sqlserver_cliente import SQLServerCliente
from core.services.sqlserver_config import SQLServerConfig


@pytest.fixture
def sqlserver_config():
    return SQLServerConfig()


@pytest.fixture
def sqlserver_config_mock():
    with patch('core.services.sqlserver_config.SQLServerConfig') as MockConfig:
        instance = MockConfig.return_value
        instance.driver = 'MockDriver'
        instance.host = 'MockHost'
        instance.database = 'MockDB'
        instance.port = 1234
        instance.user = 'MockUser'
        instance.password = 'MockPassword'
        instance.get_connection_string.return_value = 'MockConnectionString'
        yield instance


@pytest.mark.django_db
def test_sqlserver_cliente_initialization(sqlserver_config):
    cliente = SQLServerCliente(sqlserver_config)
    assert cliente is not None
    assert isinstance(cliente, SQLServerCliente)
    assert cliente.config is not None
    assert isinstance(cliente.config, SQLServerConfig)


@pytest.mark.django_db
def test_sqlserver_cliente_config_integration(sqlserver_config):
    cliente = SQLServerCliente(sqlserver_config)
    assert cliente.config == sqlserver_config
    assert cliente.config.get_connection_string() == sqlserver_config.get_connection_string()


@pytest.mark.django_db
def test_sqlserver_cliente_connect_uses_pyodbc_connect(sqlserver_config):
    cliente = SQLServerCliente(sqlserver_config)

    fake_connection = MagicMock()

    with patch("core.services.sqlserver_cliente.pyodbc.connect", return_value=fake_connection) as mock_connect:
        connection = cliente.connect()

    # Verifica se pyodbc.connect foi chamado uma vez
    mock_connect.assert_called_once()

    # Verifica se o método retornou o objeto de conexão mockado
    assert connection is fake_connection


@pytest.mark.django_db
def test_sqlserver_cliente_connect_real(sqlserver_config):
    cliente = SQLServerCliente(sqlserver_config)
    connection = cliente.connect()
    assert connection is not None
    assert hasattr(connection, 'cursor')
    
    cursor = connection.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    assert result[0] == 1
    
    connection.close()
    
@pytest.mark.django_db
def test_sqlserver_cliente_connection_context_manager(sqlserver_config_mock):
    cliente = SQLServerCliente(sqlserver_config_mock)

    fake_connection = MagicMock()
    with patch("core.services.sqlserver_cliente.pyodbc.connect", return_value=fake_connection) as mock_connect:
        with cliente.connection() as connection:
            # Dentro do contexto, a conexão deve ser o mock
            assert connection is fake_connection

        # Fora do contexto, o método close deve ter sido chamado
        fake_connection.close.assert_called_once()
    
    # Verifica se pyodbc.connect foi chamado uma vez
    mock_connect.assert_called_once()

@pytest.mark.django_db
def test_sqlserver_cliente_connection_context_manager_real(sqlserver_config):
    cliente = SQLServerCliente(sqlserver_config)

    with cliente.connection() as connection:
        assert connection is not None
        assert hasattr(connection, 'cursor')
        
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1

    # Após sair do contexto, a conexão deve estar fechada
    with pytest.raises(Exception):
        connection.cursor()  # Deve levantar uma exceção pois a conexão está fechada


@pytest.mark.django_db
def test_sqlserver_cliente_fetch_all_method_mocked(sqlserver_config_mock):
    cliente = SQLServerCliente(sqlserver_config_mock)

    fake_connection = MagicMock()
    fake_cursor = MagicMock()
    fake_cursor.description = [('column1',), ('column2',), ('column3',)]
    fake_cursor.fetchall.return_value = [(1, 'a', True), (2, 'b', False), (3, 'c', True)]
    fake_connection.cursor.return_value = fake_cursor
    
    with patch("core.services.sqlserver_cliente.pyodbc.connect", return_value=fake_connection):
        results = cliente.fetch_all("SELECT * FROM DummyTable")
    
    assert results == [
        {'column1': 1, 'column2': 'a', 'column3': True},
        {'column1': 2, 'column2': 'b', 'column3': False},
        {'column1': 3, 'column2': 'c', 'column3': True}
    ]

@pytest.mark.django_db
def test_sqlserver_cliente_fetch_all_method_empty_result(sqlserver_config_mock):
    cliente = SQLServerCliente(sqlserver_config_mock)

    fake_connection = MagicMock()
    fake_cursor = MagicMock()
    fake_cursor.description = [('column1',), ('column2',), ('column3',)]
    fake_cursor.fetchall.return_value = []
    fake_connection.cursor.return_value = fake_cursor
    
    with patch("core.services.sqlserver_cliente.pyodbc.connect", return_value=fake_connection):
        results = cliente.fetch_all("SELECT * FROM DummyTable")
    
    assert results == []

@pytest.mark.django_db
def test_sqlserver_cliente_fetch_all_method_with_params(sqlserver_config_mock):
    cliente = SQLServerCliente(sqlserver_config_mock)

    fake_connection = MagicMock()
    fake_cursor = MagicMock()
    fake_cursor.description = [('column1',), ('column2',)]
    fake_cursor.fetchall.return_value = [(10, 'x'), (20, 'y')]
    fake_connection.cursor.return_value = fake_cursor
    
    with patch("core.services.sqlserver_cliente.pyodbc.connect", return_value=fake_connection):
        results = cliente.fetch_all("SELECT * FROM DummyTable WHERE column1 > ?", [5])
    
    fake_cursor.execute.assert_called_once_with("SELECT * FROM DummyTable WHERE column1 > ?", [5])
    
    assert results == [
        {'column1': 10, 'column2': 'x'},
        {'column1': 20, 'column2': 'y'}
    ]

@pytest.mark.django_db
def test_sqlserver_cliente_fetch_all_error_handling(sqlserver_config_mock):
    cliente = SQLServerCliente(sqlserver_config_mock)

    fake_connection = MagicMock()
    fake_cursor = MagicMock()
    fake_cursor.execute.side_effect = Exception("Database error")
    fake_connection.cursor.return_value = fake_cursor
    with patch("core.services.sqlserver_cliente.pyodbc.connect", return_value=fake_connection):
        with pytest.raises(Exception) as excinfo:
            cliente.fetch_all("SELECT * FROM DummyTable")
    
    assert "Database error" in str(excinfo.value)
    
@pytest.mark.django_db
def test_sqlserver_cliente_fetch_one_method(sqlserver_config_mock):
    cliente = SQLServerCliente(sqlserver_config_mock)
    
    fake_connection = MagicMock()
    fake_cursor = MagicMock()
    fake_cursor.description = [('column1',), ('column2',)]
    fake_cursor.fetchone.return_value = ['a', 1]
    fake_connection.cursor.return_value = fake_cursor
    
    with patch("core.services.sqlserver_cliente.pyodbc.connect", return_value=fake_connection):
        result = cliente.fetch_one("SELECT * FROM DummyTable")
    
    assert result == {"column1": 'a', "column2": 1}

@pytest.mark.django_db
def test_sqlserver_cliente_fetch_one_method_empty(sqlserver_config_mock):
    cliente = SQLServerCliente(sqlserver_config_mock)
    
    fake_connection = MagicMock()
    fake_cursor = MagicMock()
    fake_cursor.description = [('column1',), ('column2',)]
    fake_cursor.fetchone.return_value = []
    fake_connection.cursor.return_value = fake_cursor
    
    with patch("core.services.sqlserver_cliente.pyodbc.connect", return_value=fake_connection):
        result = cliente.fetch_one("SELECT * FROM DummyTable")
    
    assert result is None
    
@pytest.mark.django_db
def test_sqlserver_cliente_fetch_one_method_error(sqlserver_config_mock):
    cliente = SQLServerCliente(sqlserver_config_mock)

    fake_connection = MagicMock()
    fake_cursor = MagicMock()
    fake_cursor.execute.side_effect = Exception("Database error")
    fake_connection.cursor.return_value = fake_cursor
    
    with patch("core.services.sqlserver_cliente.pyodbc.connect", return_value=fake_connection):
        with pytest.raises(Exception) as excinfo:
            cliente.fetch_one("SELECT * FROM DummyTable")
    
    assert "Database error" in str(excinfo.value)
    