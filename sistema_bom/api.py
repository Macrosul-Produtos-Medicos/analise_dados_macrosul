from django.contrib.admin.views.decorators import staff_member_required
from ninja import NinjaAPI

from core.api.logistica_api import router as logistica_router
#from core.api.financeiro_api import router as financeiro_router

api = NinjaAPI(docs_decorator=staff_member_required)

api.add_router("logistica/", logistica_router)
#api.add_router("financeiro/", financeiro_router)