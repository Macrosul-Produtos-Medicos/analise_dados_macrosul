from core.views.base import BaseProtectedView


class ListarRelacaoNotasView(BaseProtectedView):
    """List invoices relation view."""
    template_name = 'logistica/relacao_notas.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
