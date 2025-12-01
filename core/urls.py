from django.contrib import admin
from django.urls import path, include
from .views import index, tabela_exemplo, dashboard_estoque, consulta_equipamentos_pecas, ticket_medio, parceiro_de_negocio, cadastro_equipamento, revisao_de_produto, cadastro_de_pecas, pesquisa_peca

urlpatterns = [
    path('', index, name="index"),
    path('consulta_equipamentos_pecas', consulta_equipamentos_pecas, name="consulta_equipamentos_pecas"),
    path('dashboard_estoque', dashboard_estoque, name="dashboard_estoque"),
    path('tabela_exemplo', tabela_exemplo, name="tabela_exemplo"),
    path('ticket_medio', ticket_medio, name="ticket_medio"),

    path('parceiro_de_negocio', parceiro_de_negocio, name="parceiro_de_negocio"),
    path('cadastro_equipamento', cadastro_equipamento, name="cadastro_equipamento"),
    path('revisao_de_produto', revisao_de_produto, name="revisao_de_produto"),
    path('cadastro_de_pecas', cadastro_de_pecas, name="cadastro_de_pecas"),
    path('pesquisa_peca', pesquisa_peca, name="pesquisa_peca"),
]