from django.contrib import admin
from django.urls import path, include
from .views import (
    IndexView,
    TabelaExemploView,
    DashboardEstoqueView,
    ConsultaEquipamentosPecasView,
    TicketMedioView,
    ListarRelacaoNotasView,
    ListarRentabilidadeItensView
)

financeiro_patterns = [
    path('rentabilidade-itens/', ListarRentabilidadeItensView.as_view(), name="rentabilidade_itens"),
]

logistica_patterns = [
    path('', ListarRelacaoNotasView.as_view(), name="listar_relacao_notas"),
]

urlpatterns = [
    path('', IndexView.as_view(), name="index"),
    path('logistica/', include(logistica_patterns)),
    path('financeiro/', include(financeiro_patterns)),
    path('consulta_equipamentos_pecas/', ConsultaEquipamentosPecasView.as_view(), name="consulta_equipamentos_pecas"),
    path('dashboard_estoque/', DashboardEstoqueView.as_view(), name="dashboard_estoque"),
    path('tabela_exemplo/', TabelaExemploView.as_view(), name="tabela_exemplo"),
    path('ticket_medio/', TicketMedioView.as_view(), name="ticket_medio"),

    # path('parceiro_de_negocio/', ParceiroDeNegocioView.as_view(), name="parceiro_de_negocio"),
    # path('cadastro_equipamento/', CadastroEquipamentoView.as_view(), name="cadastro_equipamento"),
    # path('revisao_de_produto/', RevisaoDeProdutoView.as_view(), name="revisao_de_produto"),
    # path('cadastro_de_pecas/', CadastroDePecasView.as_view(), name="cadastro_de_pecas"),
    # path('pesquisa_peca/', PesquisaPecaView.as_view(), name="pesquisa_peca"),
]