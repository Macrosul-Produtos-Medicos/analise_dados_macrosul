import pytest
import pandas as pd
import numpy as np

from core.services.base_service import BaseService

from core.services.exceptions import DataNotFoundError


@pytest.fixture
def base_service():
    return BaseService()


@pytest.fixture
def sample_data():
    """Sample data simulating sales by product and month."""
    return pd.DataFrame([
        {"Produto": "A", "Mes": "Jan", "Quantidade": 10},
        {"Produto": "A", "Mes": "Fev", "Quantidade": 15},
        {"Produto": "A", "Mes": "Mar", "Quantidade": 20},
        {"Produto": "B", "Mes": "Jan", "Quantidade": 5},
        {"Produto": "B", "Mes": "Fev", "Quantidade": 8},
        {"Produto": "B", "Mes": "Mar", "Quantidade": 12},
        {"Produto": "C", "Mes": "Jan", "Quantidade": 7},
        {"Produto": "C", "Mes": "Fev", "Quantidade": 9},
        {"Produto": "C", "Mes": "Mar", "Quantidade": 11},
    ])
    
class TestBaseServiceDataFrameToListDicts:
    """Test cases for BaseService.dataframe_to_list_dicts method."""
    
    def test_dataframe_to_list_dicts_returns_list(self, base_service, sample_data):
        """Should return a list of dictionaries."""
        result = base_service.dataframe_to_list_dicts(sample_data)
        assert isinstance(result, list)
        assert all(isinstance(item, dict) for item in result)
    
    def test_dataframe_to_list_dicts_correct_length(self, base_service, sample_data):
        """Should return list with correct number of items."""
        result = base_service.dataframe_to_list_dicts(sample_data)
        assert len(result) == len(sample_data)
    
    def test_dataframe_to_list_dicts_correct_content(self, base_service, sample_data):
        """Should return list with correct content."""
        result = base_service.dataframe_to_list_dicts(sample_data)
        for i, row in sample_data.iterrows():
            assert result[i] == row.to_dict()


class TestBaseServiceListDictsToDataFrame:
    """Test cases for BaseService.list_dicts_to_dataframe method."""
    
    def test_list_dicts_to_dataframe_returns_dataframe(self, base_service):
        """Should return a pandas DataFrame."""
        data = [
            {"Col1": 1, "Col2": "A"},
            {"Col1": 2, "Col2": "B"},
            {"Col1": 3, "Col2": "C"},
        ]
        result = base_service.list_dicts_to_dataframe(data)
        assert isinstance(result, pd.DataFrame)
    
    def test_list_dicts_to_dataframe_has_correct_shape(self, base_service):
        """Should have correct number of rows and columns."""
        data = [
            {"Col1": 1, "Col2": "A"},
            {"Col1": 2, "Col2": "B"},
            {"Col1": 3, "Col2": "C"},
        ]
        result = base_service.list_dicts_to_dataframe(data)
        assert result.shape == (3, 2)  # 3 rows, 2 columns
    
    def test_list_dicts_to_dataframe_with_empty_list(self, base_service):
        """Should return empty DataFrame for empty list."""
        data = []
        result = base_service.list_dicts_to_dataframe(data)
        assert isinstance(result, pd.DataFrame)
        assert result.empty


class TestBaseServicePivotTable:
    """Test cases for BaseService.pivot_table method."""
    
    def test_pivot_table_returns_dataframe(self, base_service, sample_data):
        """Should return a pandas DataFrame."""
        result = base_service.pivot_table(
            data=sample_data,
            index=["Produto"],
            columns="Mes",
            values="Quantidade"
        )
        assert isinstance(result, pd.DataFrame)
    
    def test_pivot_table_has_correct_columns(self, base_service, sample_data):
        """Should have index column + pivoted columns."""
        result = base_service.pivot_table(
            data=sample_data,
            index=["Produto"],
            columns="Mes",
            values="Quantidade"
        )
        # Should have: Produto, Jan, Fev, Mar
        assert "Produto" in result.columns
        assert "Jan" in result.columns
        assert "Fev" in result.columns
        assert "Mar" in result.columns
    
    def test_pivot_table_has_correct_row_count(self, base_service, sample_data):
        """Should have one row per unique index value."""
        result = base_service.pivot_table(
            data=sample_data,
            index=["Produto"],
            columns="Mes",
            values="Quantidade"
        )
        # 3 unique products: A, B, C
        assert len(result) == 3
    
    def test_pivot_table_aggregates_values_correctly(self, base_service, sample_data):
        """Should aggregate values correctly using default sum."""
        result = base_service.pivot_table(
            data=sample_data,
            index=["Produto"],
            columns="Mes",
            values="Quantidade"
        )
        # Check specific values
        produto_a = result[result["Produto"] == "A"].iloc[0]
        assert produto_a["Jan"] == 10
        assert produto_a["Fev"] == 15
        assert produto_a["Mar"] == 20
    
    def test_pivot_table_with_multiple_index_columns(self, base_service):
        """Should work with multiple index columns."""
        data = pd.DataFrame([
            {"Regiao": "Sul", "Produto": "A", "Mes": "Jan", "Quantidade": 10},
            {"Regiao": "Sul", "Produto": "A", "Mes": "Fev", "Quantidade": 15},
            {"Regiao": "Norte", "Produto": "A", "Mes": "Jan", "Quantidade": 20},
            {"Regiao": "Norte", "Produto": "A", "Mes": "Fev", "Quantidade": 25},
        ])
        result = base_service.pivot_table(
            data=data,
            index=["Regiao", "Produto"],
            columns="Mes",
            values="Quantidade"
        )
        assert "Regiao" in result.columns
        assert "Produto" in result.columns
        assert len(result) == 2  # Sul-A and Norte-A
    
    def test_pivot_table_with_custom_aggfunc(self, base_service):
        """Should use custom aggregation function."""
        data = pd.DataFrame([
            {"Produto": "A", "Mes": "Jan", "Quantidade": 10},
            {"Produto": "A", "Mes": "Jan", "Quantidade": 20},  # duplicate to test aggregation
            {"Produto": "A", "Mes": "Fev", "Quantidade": 15},
        ])
        result = base_service.pivot_table(
            data=data,
            index=["Produto"],
            columns="Mes",
            values="Quantidade",
            aggfunc="mean"  # Use mean instead of sum
        )
        produto_a = result[result["Produto"] == "A"].iloc[0]
        assert produto_a["Jan"] == 15.0  # (10 + 20) / 2 = 15
        assert produto_a["Fev"] == 15.0
    
    def test_pivot_table_with_sum_aggregation(self, base_service):
        """Should sum values when there are duplicates."""
        data = pd.DataFrame([
            {"Produto": "A", "Mes": "Jan", "Quantidade": 10},
            {"Produto": "A", "Mes": "Jan", "Quantidade": 20},  # duplicate
        ])
        result = base_service.pivot_table(
            data=data,
            index=["Produto"],
            columns="Mes",
            values="Quantidade",
            aggfunc="sum"
        )
        produto_a = result[result["Produto"] == "A"].iloc[0]
        assert produto_a["Jan"] == 30  # 10 + 20
    
    def test_pivot_table_fill_value_for_missing_data(self, base_service):
        """Should fill missing values with fill_value."""
        data = pd.DataFrame([
            {"Produto": "A", "Mes": "Jan", "Quantidade": 10},
            # Produto A has no Fev data
            {"Produto": "B", "Mes": "Jan", "Quantidade": 5},
            {"Produto": "B", "Mes": "Fev", "Quantidade": 8},
        ])
        result = base_service.pivot_table(
            data=data,
            index=["Produto"],
            columns="Mes",
            values="Quantidade",
            fill_value=0
        )
        produto_a = result[result["Produto"] == "A"].iloc[0]
        assert produto_a["Fev"] == 0  # Missing data filled with 0
    
    def test_pivot_table_custom_fill_value(self, base_service):
        """Should use custom fill_value."""
        data = pd.DataFrame([
            {"Produto": "A", "Mes": "Jan", "Quantidade": 10},
            {"Produto": "B", "Mes": "Fev", "Quantidade": 8},
        ])
        result = base_service.pivot_table(
            data=data,
            index=["Produto"],
            columns="Mes",
            values="Quantidade",
            fill_value=-1  # Custom fill value
        )
        produto_a = result[result["Produto"] == "A"].iloc[0]
        assert produto_a["Fev"] == -1
    
    def test_pivot_table_no_columns_name(self, base_service, sample_data):
        """Should remove the columns.name attribute."""
        result = base_service.pivot_table(
            data=sample_data,
            index=["Produto"],
            columns="Mes",
            values="Quantidade"
        )
        assert result.columns.name is None
    
    def test_pivot_table_reset_index(self, base_service, sample_data):
        """Should reset index (index becomes a regular column)."""
        result = base_service.pivot_table(
            data=sample_data,
            index=["Produto"],
            columns="Mes",
            values="Quantidade"
        )
        # After reset_index, the index should be the default RangeIndex
        assert isinstance(result.index, pd.RangeIndex)
        # And "Produto" should be a column, not the index
        assert "Produto" in result.columns
    
    def test_pivot_table_with_empty_data_raises_error(self, base_service):
        """Should raise ValueError for empty DataFrame."""
        with pytest.raises(DataNotFoundError) as exc_info:
            base_service.pivot_table(
                data=pd.DataFrame(),
                index=["Produto"],
                columns="Mes",
                values="Quantidade"
            )
        assert "No data available to pivot." in str(exc_info.value)
    
    def test_pivot_table_with_single_row(self, base_service):
        """Should work with a single row of data."""
        data = pd.DataFrame([{"Produto": "A", "Mes": "Jan", "Quantidade": 10}])
        result = base_service.pivot_table(
            data=data,
            index=["Produto"],
            columns="Mes",
            values="Quantidade"
        )
        assert len(result) == 1
        assert result.iloc[0]["Jan"] == 10
