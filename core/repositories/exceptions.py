class RepositoryError(Exception):
    """Exceção base para erros de repositório."""
    pass


class ConnectionError(RepositoryError):
    """Erro de conexão com o banco de dados."""
    pass


class QueryError(RepositoryError):
    """Erro na execução da query."""
    pass