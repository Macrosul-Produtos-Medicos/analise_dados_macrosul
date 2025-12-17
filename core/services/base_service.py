import pandas as pd
import numpy as np

from typing import Any, Dict, List, TypeVar, Generic, Callable
from dataclasses import dataclass

from core.services.sqlserver_cliente import SQLServerCliente, default_sql_server_client

from core.services.exceptions import DataNotFoundError


class BaseService:
    """
    Base service with common functionality.
    All services should inherit from this class.
    """
    
    def dataframe_to_list_dicts(self, dataframe: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Convert a pandas DataFrame to a list of dictionaries.
        
        :param dataframe: DataFrame representing the data.
        :return: List of dictionaries representing the data.
        """
        return dataframe.to_dict(orient="records")
    
    
    def list_dicts_to_dataframe(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Convert a list of dictionaries to a pandas DataFrame.
        
        :param data: List of dictionaries representing the data.
        :return: DataFrame representing the data.
        """
        return pd.DataFrame(data)
    
    def pivot_table(
        self,
        data: pd.DataFrame,
        index: List[str],
        columns: str,
        values: str,
        aggfunc: str | Callable = "sum",
        fill_value: Any = 0
    ) -> pd.DataFrame:
        """
        Pivot a DataFrame into a pivoted DataFrame.
        
        :param data: DataFrame representing the data.
        :param index: List of columns to set as index.
        :param columns: Column to pivot.
        :param values: Column with values to aggregate.
        :param aggfunc: Aggregation function to use.
        :param fill_value: Value to replace NaNs with.
        :return: Pivoted DataFrame.
        :raises ValueError: If data is empty.
        """
        if data.empty:
            raise DataNotFoundError("No data available to pivot.")
        

        pivot_df = pd.pivot_table(
            data,
            index=index,
            columns=columns,
            values=values,
            aggfunc=aggfunc,
            fill_value=fill_value
        )
        pivot_df.reset_index(inplace=True)
        
        # Flatten MultiIndex columns if they exist (e.g., from multi-column pivot)
        if isinstance(pivot_df.columns, pd.MultiIndex):
            pivot_df.columns = [
                '-'.join(str(c) for c in col).strip('-') if isinstance(col, tuple) else col
                for col in pivot_df.columns.values
            ]
        
        pivot_df.columns.name = None  # Remove the aggregation name
        return pivot_df
