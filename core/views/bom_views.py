from .base import BaseProtectedView


class ParceiroDeNegocioView(BaseProtectedView):
    """Business partner form view."""
    template_name = 'BOM/parceiro_de_negocio.html'


class CadastroEquipamentoView(BaseProtectedView):
    """Equipment registration form view."""
    template_name = 'BOM/cadastro_equipamento.html'


class RevisaoDeProdutoView(BaseProtectedView):
    """Product revision form view."""
    template_name = 'BOM/revisao_de_produto.html'


class CadastroDePecasView(BaseProtectedView):
    """Parts registration form view."""
    template_name = 'BOM/cadastro_de_pecas.html'


class PesquisaPecaView(BaseProtectedView):
    """Parts search form view."""
    template_name = 'BOM/pesquisa_peca.html'
