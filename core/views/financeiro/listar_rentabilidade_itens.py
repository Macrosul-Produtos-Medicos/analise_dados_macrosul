from core.views.base import BaseProtectedView

class ListarRentabilidadeItensView(BaseProtectedView):
    """List item traceability view."""
    template_name = 'financeiro/rentabilidade_itens.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context