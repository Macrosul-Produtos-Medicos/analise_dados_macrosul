from http import HTTPStatus
from django.http import HttpRequest

from ninja import Router
from core.services.logistica_service import LogisticaService

from .decorators import handle_error

router = Router(tags=["Logística"])

@router.get("/listar-transportadoras-mais-usadas/", response={HTTPStatus.OK: list[dict]})
@handle_error
def listar_transportadoras_mais_usadas(request: HttpRequest, offset : int = 10, fetch_next: int = None):
    service = LogisticaService()
    transportadoras, _ = service.listar_transportadoras_mais_usadas(offset=offset, fetch_next=fetch_next)
    return transportadoras