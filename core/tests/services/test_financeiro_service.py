import pytest

from core.services.financeiro_service import FinanceiroService
from core.repositories.financeiro_repository import FinanceiroRepository
from core.services.exceptions import (
    ServiceError,
    ValidationError,
    BusinessRuleError,
    DataNotFoundError,
    DataTransformationError,
)


class TestFinanceiroService:
    
    def test_financeiro_service_initialization(self):
        """Test the initialization of FinanceiroService."""
        
        service = FinanceiroService()
        assert service is not None
        assert service.repo is not None  # Assuming the service has a config attribute
        assert isinstance(service.repo, FinanceiroRepository)  # Assuming the repository class is FinanceiroRepository
    
    def test_financeiro_repository_initialization_error_handling(self):
        """Test the initialization of FinanceiroRepository and error handling."""
        
        # Mock the repository to raise an exception during initialization
        original_init = FinanceiroRepository.__init__
        def mock_init(self):
            raise Exception("Initialization error")
        
        FinanceiroRepository.__init__ = mock_init
        with pytest.raises(Exception) as exc_info:
            repo = FinanceiroRepository()
            
        # Restore the original __init__ method
        FinanceiroRepository.__init__ = original_init
        

@pytest.fixture
def financeiro_service():
    return FinanceiroService()


@pytest.fixture
def listar_rentabilidade_itens_mock():
    """Mock data for listar_rentabilidade_itens."""
    return [
        {
            "ItemCode": "A001",
            "ItemName": "Produto A",
            "TipoDoNegocio": "B2B",
            "Quantidade": 100,
            "PrecoMinimoUnitario": 50.0,
            "FaturamentoPorItem": 5000.0,
            "Rentabilidade": -0.05,
        },
        {
            "ItemCode": "A001",
            "ItemName": "Produto A",
            "TipoDoNegocio": "B2C",
            "Quantidade": 200,
            "PrecoMinimoUnitario": 50.0,
            "FaturamentoPorItem": 10000.0,
            "Rentabilidade": -0.05,
        },
        {
            "ItemCode": "B002",
            "ItemName": "Produto B",
            "TipoDoNegocio": "B2B",
            "Quantidade": 150,
            "PrecoMinimoUnitario": 30.0,
            "FaturamentoPorItem": 4500.0,
            "Rentabilidade": 0.10,
        },
        {
            "ItemCode": "B002",
            "ItemName": "Produto B",
            "TipoDoNegocio": "B2C",
            "Quantidade": 100,
            "PrecoMinimoUnitario": 30.0,
            "FaturamentoPorItem": 3000.0,
            "Rentabilidade": 0.10,
        },
    ]

class TestListarRentabilidadeItens:
    
    def test_listar_rentabilidade_itens_default_response(self, financeiro_service, listar_rentabilidade_itens_mock):
        """Test the listar_rentabilidade_itens method of FinanceiroService."""
        
        # Mock the repository method to return the mock data
        financeiro_service.repo.cliente.fetch_all = lambda sql, params=None: listar_rentabilidade_itens_mock
        result, sql = financeiro_service.listar_rentabilidade_itens()
        assert result == listar_rentabilidade_itens_mock
        assert 'DECLARE @DataFim DATE = GETDATE();' in sql                          # Check if default SQL date is used
        assert 'DECLARE @DataInicio DATE = DATEADD(MONTH, -12, GETDATE());' in sql  # Check if default SQL date is used
        
    def test_listar_rentabilidade_itens_with_date_range(self, financeiro_service, listar_rentabilidade_itens_mock):
        """Test the listar_rentabilidade_itens method with specific date range."""
        
        # Mock the repository method to return the mock data
        financeiro_service.repo.cliente.fetch_all = lambda sql, params=None: listar_rentabilidade_itens_mock
        
        data_inicio = "2023-05-01"
        data_fim = "2023-07-03"
        
        result, sql = financeiro_service.listar_rentabilidade_itens(data_inicio=data_inicio, data_fim=data_fim)
        assert result == listar_rentabilidade_itens_mock
        assert f"DECLARE @DataFim DATE = '{data_fim}';" in sql
        assert f"DECLARE @DataInicio DATE = '{data_inicio}';" in sql
    
    def test_listar_rentabilidade_itens_invalid_date_range(self, financeiro_service):
        """Test the listar_rentabilidade_itens method with invalid date range."""
        
        data_inicio = "2023-08-01"
        data_fim = "2023-07-01"  # End date before start date
        
        expected_exception = ServiceError  # Assuming the service raises ServiceError for invalid date ranges
        
        with pytest.raises(expected_exception):
            financeiro_service.listar_rentabilidade_itens(data_inicio=data_inicio, data_fim=data_fim)
            
    def test_listar_rentabilidade_itens_repository_invalid_data(self, financeiro_service, listar_rentabilidade_itens_mock):
        """Test the listar_rentabilidade_itens method with repository returning invalid data."""
        
        data_inicio = "invalid-date"
        data_fim = "2023-07-01"
        
        # Mock the repository method to return invalid data
        financeiro_service.repo.cliente.fetch_all = lambda sql, params=None: listar_rentabilidade_itens_mock
        expected_exception = ServiceError  # Assuming the service raises ServiceError for invalid data
        with pytest.raises(expected_exception) as exc_info:
            financeiro_service.listar_rentabilidade_itens(data_inicio=data_inicio, data_fim=data_fim)
            assert "Erro ao executar consulta" in str(exc_info.value)
            
    @pytest.mark.parametrize("repository_exception, expected_exception, error_message", [
        (RepoConnectionError, ServiceError, "Erro de conexão com o banco de dados"),
        (RepoQueryError, ServiceError, "Erro ao executar consulta"),
        (RepositoryError, ServiceError, "Erro no repositório"),
        (Exception, ServiceError, "Erro inesperado no serviço"),
    ])
    def test_listar_rentabilidade_itens_handling_repository_exceptions(self, financeiro_service, repository_exception, expected_exception, error_message):
        
        
        
        
        
        
        
        
        
            
    