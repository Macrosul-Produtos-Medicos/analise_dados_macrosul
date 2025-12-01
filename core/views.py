from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    return render(request,'index.html')

@login_required
def tabela_exemplo(request):
    return render(request,'tabela_exemplo.html')

@login_required
def dashboard_estoque(request):
    return render(request,'dashboard_estoque.html')

@login_required
def consulta_equipamentos_pecas(request):
    return render(request,'consulta_equipamentos_pecas.html')

@login_required
def ticket_medio(request):
    return render(request,'ticket_medio.html')

# VIEWS DOS FORMULÁRIOS
@login_required
def parceiro_de_negocio(request):
    return render(request, 'BOM/parceiro_de_negocio.html')

@login_required
def cadastro_equipamento(request):
    return render(request, 'BOM/cadastro_equipamento.html')

@login_required
def revisao_de_produto(request):
    return render(request, 'BOM/revisao_de_produto.html')

@login_required
def cadastro_de_pecas(request):
    return render(request, 'BOM/cadastro_de_pecas.html')

@login_required
def pesquisa_peca(request):
    return render(request, 'BOM/pesquisa_peca.html')