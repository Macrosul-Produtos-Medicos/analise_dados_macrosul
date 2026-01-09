from core.repositories.financeiro_repository import FinanceiroRepository
from .decorators import handle_service_errors

class FinanceiroService:
    def __init__(self):
        self.repo = FinanceiroRepository()
    
    @handle_service_errors
    def listar_rentabilidade_itens(self, data_inicio: str | None = None, data_fim: str | None = None) -> tuple[list[dict], str]:
        result, sql = self.repo.listar_rentabilidade_itens(data_inicio=data_inicio, data_fim=data_fim)
        return result, sql
        