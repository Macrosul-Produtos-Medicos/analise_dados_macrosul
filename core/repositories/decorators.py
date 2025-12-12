import functools
import pyodbc
from .exceptions import ConnectionError, QueryError, RepositoryError
def handle_db_errors(func):
    """
    Decorator que trata exceções de pyodbc e as transforma
    em exceções mais amigáveis para a camada de serviço.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        
        except pyodbc.InterfaceError as e:
            raise ConnectionError(f"Falha na configuração do driver ODBC: {e}") from e
        
        except pyodbc.OperationalError as e:
            raise ConnectionError(f"Não foi possível conectar ao SQL Server: {e}") from e
        
        except pyodbc.ProgrammingError as e:
            raise QueryError(f"Erro na query SQL: {e}") from e
        
        except pyodbc.DataError as e:
            raise QueryError(f"Erro de dados na query: {e}") from e
        
        except pyodbc.DatabaseError as e:
            raise RepositoryError(f"Erro no banco de dados: {e}") from e
        except ValueError as e:
            raise QueryError(f"Erro de valor: {e}") from e
        except Exception as e:
            raise RepositoryError(f"Erro inesperado no repositório: {e}") from e
    
    return wrapper