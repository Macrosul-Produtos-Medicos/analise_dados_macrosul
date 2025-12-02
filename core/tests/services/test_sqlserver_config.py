import pytest
from django.conf import settings

from core.services.sqlserver_config import SQLServerConfig

@pytest.mark.django_db
def test_sqlserver_config_initialization():
    config = SQLServerConfig()
    assert config is not None
    

@pytest.mark.django_db
def test_sqlserver_config_attributes():
    config = SQLServerConfig()
    # Assuming SQLServerConfig has attributes like host, port, user, password
    assert config is not None
    assert hasattr(config, 'driver')
    assert hasattr(config, 'host')
    assert hasattr(config, 'database')
    assert hasattr(config, 'port')
    assert hasattr(config, 'user')
    assert hasattr(config, 'password')
    
@pytest.mark.django_db
def test_sqlserver_config_default_values():
    config = SQLServerConfig()
    # Check if default values are set correctly (assuming they are empty strings)
    assert config.driver == settings.SQLSERVER_DRIVER 
    assert config.host == settings.SQLSERVER_HOST
    assert config.database == settings.SQLSERVER_DB
    assert config.port == settings.SQLSERVER_PORT
    assert config.user == settings.SQLSERVER_USER
    assert config.password == settings.SQLSERVER_PASSWORD
    
@pytest.mark.django_db
def test_sqlserver_config_connection_parameters():
    config = SQLServerConfig()
    # Validate that connection parameters are not None or empty
    assert config.driver is not None and config.driver != ''
    assert config.host is not None and config.host != ''
    assert config.database is not None and config.database != ''
    assert config.port is not None and config.port != ''
    assert config.user is not None and config.user != ''
    assert config.password is not None and config.password != ''
    
@pytest.mark.django_db
def test_get_sqlserver_connection_string():
    config = SQLServerConfig()
    connection_string = config.get_connection_string()
    assert isinstance(connection_string, str)
    assert 'DRIVER=' in connection_string
    assert 'SERVER=' in connection_string
    assert 'DATABASE=' in connection_string
    assert 'UID=' in connection_string
    assert 'PWD=' in connection_string
    assert 'PORT=' in connection_string
    assert connection_string == f'DRIVER={config.driver};SERVER={config.host},{config.port};DATABASE={config.database};UID={config.user};PWD={config.password};PORT={config.port};'
    
    