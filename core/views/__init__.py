# Base view
from .base import BaseProtectedView

# Dashboard views
from .dashboard_views import (
    IndexView,
    TabelaExemploView,
    DashboardEstoqueView,
    ConsultaEquipamentosPecasView,
    TicketMedioView,
)

# Logistica views
from .logistica import (
    ListarRelacaoNotasView,
)

# Financeiro views
from .financeiro import (
    ListarRentabilidadeItensView,
)
