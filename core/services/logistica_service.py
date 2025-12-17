from core.repositories.logistica_repository import LogisticaRepository
from core.services.decorators import handle_service_errors, validate_pagination

from core.services.base_service import BaseService

class LogisticaService(BaseService):
    def __init__(self):
        self.repo = LogisticaRepository()
    
    @handle_service_errors
    @validate_pagination
    def listar_transportadoras_mais_usadas(self, offset: int = 0, fetch_next: int = None) -> tuple[list[dict], str]:
        data, sql = self.repo.listar_transportadoras_mais_usadas(offset=offset, fetch_next=fetch_next)
        dataframe = self.list_dicts_to_dataframe(data)
        dataframe = self.pivot_table(
            data=dataframe,
            index=["CardCode", "CardName"],
            columns=["Mes", "Ano"],
            values="Total",
            aggfunc="sum",
            fill_value=0
        )
        data = self.dataframe_to_list_dicts(dataframe)
        return data, sql