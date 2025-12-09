from contextlib import contextmanager
import pyodbc
from typing import Any, Dict, Iterable, List

from .sqlserver_config import SQLServerConfig
class SQLServerCliente:
    def __init__(self, config: Any):
        self.config = config
        
    def connect(self) -> pyodbc.Connection:
        connection_string = self.config.get_connection_string()
        connection = pyodbc.connect(connection_string)
        return connection
    
    @contextmanager
    def connection(self):
        connection = self.connect()
        try:
            yield connection
        finally:
            connection.close()
            
    def fetch_all(self, query: str, params: Iterable[Any] | None = None) -> List[Dict[str, Any]]:
        params = params or []
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    
    def fetch_one(self, query: str, params: Iterable[Any] | None = None) -> Dict[str, Any] | None:
        params = params or []
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            if not row:
                return None
            
            columns = [col[0] for col in cursor.description]
        return dict(zip(columns, row))
    
default_sql_server_client = SQLServerCliente(SQLServerConfig())