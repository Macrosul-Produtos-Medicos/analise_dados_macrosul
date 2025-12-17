import pytest
from unittest.mock import patch
from ninja.testing import TestClient

from core.api.logistica_api import router as logistica_router

from core.services.exceptions import (
    ServiceError,
    ValidationError,
    BusinessRuleError,
    DataNotFoundError,
    DataTransformationError,
)


@pytest.fixture
def api_client():
    return TestClient(logistica_router)


@pytest.fixture
def listar_transportadoras_mais_usadas_mock():
    """Expected data after pivot transformation in service."""
    return [
        {"CardCode": "F00001", "CardName": "Transportadora A", "1-2024": 150, "1-2025": 0, "2-2025": 0},
        {"CardCode": "F00002", "CardName": "Transportadora B", "1-2024": 120, "1-2025": 0, "2-2025": 0},
        {"CardCode": "F00003", "CardName": "Transportadora C", "1-2024": 0, "1-2025": 120, "2-2025": 0},
        {"CardCode": "F00004", "CardName": "Transportadora D", "1-2024": 0, "1-2025": 0, "2-2025": 120},
    ]


class TestLogisticaAPI:

    def test_listar_transportadoras_mais_usadas(
        self,
        api_client,
        listar_transportadoras_mais_usadas_mock
    ):
        """Test the API endpoint for listing most used carriers."""
        # Mock the service method using patch
        with patch('core.api.logistica_api.LogisticaService') as MockService:
            mock_instance = MockService.return_value
            mock_instance.listar_transportadoras_mais_usadas.return_value = (
                listar_transportadoras_mais_usadas_mock,
                "SELECT ..."
            )

            # Make the API call (without leading slash for TestClient)
            response = api_client.get("listar-transportadoras-mais-usadas/")

            # Validate the response
            assert response.status_code == 200
            assert response.json() == listar_transportadoras_mais_usadas_mock
    
    def test_listar_transportadoras_mais_usadas_offset_fetch_next(
        self,
        api_client,
        listar_transportadoras_mais_usadas_mock
    ):
        """Test the API endpoint with offset and fetch_next parameters."""
        offset = 5
        fetch_next = 10

        with patch('core.api.logistica_api.LogisticaService') as MockService:
            mock_instance = MockService.return_value
            mock_instance.listar_transportadoras_mais_usadas.return_value = (
                listar_transportadoras_mais_usadas_mock,
                "SELECT ..."
            )

            # Make the API call with query parameters in URL
            response = api_client.get(
                f"listar-transportadoras-mais-usadas/?offset={offset}&fetch_next={fetch_next}"
            )

            # Validate the response
            assert response.status_code == 200
            assert response.json() == listar_transportadoras_mais_usadas_mock

            # Ensure the service method was called with correct parameters
            mock_instance.listar_transportadoras_mais_usadas.assert_called_once_with(
                offset=offset,
                fetch_next=fetch_next
            )
        
    def test_listar_transportadoras_mais_usadas_invalid_params(self, api_client):
        """Test the API endpoint with invalid pagination parameters."""
        # Test with negative offset
        response = api_client.get("listar-transportadoras-mais-usadas/?offset=-1&fetch_next=10")
        assert response.status_code == 422  # Unprocessable Entity

        # Test with zero fetch_next
        response = api_client.get("listar-transportadoras-mais-usadas/?offset=0&fetch_next=0")
        assert response.status_code == 422  # Unprocessable Entity
    
    @pytest.mark.parametrize("service_exception, expected_status, expected_message", [
        (ServiceError("Invalid data"), 503, "Erro no serviço"),
        (ValidationError("Data not found"), 422, "Erro de validação"),
        (BusinessRuleError("Service failure"), 400, "Erro de regra de negócio"),
        (DataNotFoundError("Service failure"), 404, "Dados não encontrados"),
        (DataTransformationError("Service failure"), 500, "Erro na transformação de dados"),
        (Exception("Service failure"), 500, "Erro interno do servidor"),
    ])    
    def test_listar_transportadoras_mais_usadas_test_error_handling(self, api_client, service_exception, expected_status, expected_message):
        """Test error handling in the API endpoint."""
        with patch('core.api.logistica_api.LogisticaService') as MockService:
            mock_instance = MockService.return_value
            mock_instance.listar_transportadoras_mais_usadas.side_effect = service_exception

            # Make the API call
            response = api_client.get("listar-transportadoras-mais-usadas/")

            # Validate the response
            assert response.status_code == expected_status
            response_data = response.json()
            assert response_data['error'] is True
            assert response_data['message'] == expected_message
            
    def test_listar_transportadoras_mais_usadas_no_data(self, api_client):
        """Test the API endpoint when no data is found."""
        with patch('core.api.logistica_api.LogisticaService') as MockService:
            mock_instance = MockService.return_value
            mock_instance.listar_transportadoras_mais_usadas.return_value = ([], "SELECT ...")

            # Make the API call
            response = api_client.get("listar-transportadoras-mais-usadas/")

            # Validate the response
            assert response.status_code == 200
            assert response.json() == []
    
    
        
    