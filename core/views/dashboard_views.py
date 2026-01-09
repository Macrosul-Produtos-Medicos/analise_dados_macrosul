from .base import BaseProtectedView


class IndexView(BaseProtectedView):
    """Home page view."""
    template_name = 'index.html'


class TabelaExemploView(BaseProtectedView):
    """Example table view."""
    template_name = 'tabela_exemplo.html'


class DashboardEstoqueView(BaseProtectedView):
    """Stock dashboard view."""
    template_name = 'dashboard_estoque.html'


class ConsultaEquipamentosPecasView(BaseProtectedView):
    """Equipment and parts query view."""
    template_name = 'consulta_equipamentos_pecas.html'


class TicketMedioView(BaseProtectedView):
    """Average ticket view."""
    template_name = 'ticket_medio.html'
