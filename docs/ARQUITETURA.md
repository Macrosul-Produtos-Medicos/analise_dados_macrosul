# 📊 Documentação do Projeto - Análise de Dados Macrosul

## Visão Geral

O **Análise de Dados Macrosul** é uma aplicação web desenvolvida em Django para análise de dados empresariais, focada em módulos de **Logística** e **Financeiro**. O sistema segue uma arquitetura em camadas bem definida, facilitando manutenção, testes e escalabilidade.

---

## 🏗️ Arquitetura em Camadas

O projeto segue o padrão de arquitetura em camadas (Layered Architecture), separando responsabilidades de forma clara e organizada:

```
┌─────────────────────────────────────────────────────────────────┐
│                        CAMADA DE APRESENTAÇÃO                   │
│  ┌─────────────────────────┐    ┌─────────────────────────────┐ │
│  │       Views (HTML)      │    │      API (REST/Ninja)       │ │
│  │   core/views/           │    │      core/api/              │ │
│  └───────────┬─────────────┘    └──────────────┬──────────────┘ │
└──────────────┼─────────────────────────────────┼────────────────┘
               │                                 │
               ▼                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                        CAMADA DE SERVIÇOS                       │
│                       core/services/                            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  • Regras de Negócio                                      │  │
│  │  • Transformação de Dados (pandas)                        │  │
│  │  • Validações                                             │  │
│  │  • Orquestração                                           │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CAMADA DE REPOSITÓRIOS                     │
│                      core/repositories/                         │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  • Acesso a Dados                                         │  │
│  │  • Queries SQL                                            │  │
│  │  • Abstração do Banco de Dados                            │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CAMADA DE INFRAESTRUTURA                   │
│                       core/services/                            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  • SQLServerCliente (conexão com banco)                   │  │
│  │  • Configurações de conexão                               │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Estrutura de Diretórios

```
analise_dados_macrosul/
├── manage.py                    # Entrada principal do Django
├── requirements.txt             # Dependências do projeto
├── pytest.ini                   # Configurações de testes
│
├── sistema_bom/                 # Configurações do projeto Django
│   ├── settings.py              # Configurações gerais
│   ├── urls.py                  # Rotas principais
│   ├── api.py                   # Configuração do Django Ninja API
│   ├── wsgi.py                  # Servidor WSGI
│   └── asgi.py                  # Servidor ASGI
│
├── core/                        # Aplicação principal
│   ├── api/                     # 🌐 Camada de API REST
│   ├── services/                # ⚙️ Camada de Serviços
│   ├── repositories/            # 💾 Camada de Repositórios
│   ├── views/                   # 🖥️ Camada de Apresentação (Views)
│   ├── helpers/                 # 🛠️ Utilitários
│   ├── templates/               # 📄 Templates HTML
│   ├── tests/                   # 🧪 Testes automatizados
│   ├── models.py                # Modelos Django (ORM)
│   └── urls.py                  # Rotas do core
│
├── static/                      # Arquivos estáticos
│   ├── css/                     # Estilos
│   └── js/                      # JavaScript
│
├── templates/                   # Templates globais
│   ├── base.html                # Template base
│   └── account/                 # Templates de autenticação
│
└── docs/                        # Documentação
```

---

## 🔵 Camada de Apresentação (Presentation Layer)

### Views (Templates)

**Localização:** `core/views/`

Responsável por renderizar páginas HTML. Todas as views protegidas herdam de `BaseProtectedView`:

```python
# core/views/base.py
class BaseProtectedView(LoginRequiredMixin, TemplateView):
    """
    Base view que requer autenticação.
    Todas as views protegidas devem herdar desta classe.
    """
    login_url = '/accounts/login/'
    redirect_field_name = 'next'
```

**Organização por módulos:**
- `core/views/financeiro/` - Views do módulo financeiro
- `core/views/logistica/` - Views do módulo logística
- `core/views/dashboard_views.py` - Views de dashboards gerais

**Exemplo de View:**
```python
# core/views/financeiro/listar_rentabilidade_itens.py
class ListarRentabilidadeItensView(BaseProtectedView):
    """View para listar rentabilidade de itens."""
    template_name = 'financeiro/rentabilidade_itens.html'
```

### API REST (Django Ninja)

**Localização:** `core/api/`

O projeto utiliza o **Django Ninja** para APIs REST, proporcionando documentação automática e tipagem forte.

**Configuração central:**
```python
# sistema_bom/api.py
from ninja import NinjaAPI

api = NinjaAPI(docs_decorator=staff_member_required)
api.add_router("logistica/", logistica_router)
```

**Exemplo de endpoint:**
```python
# core/api/logistica_api.py
from ninja import Router
from core.services.logistica_service import LogisticaService

router = Router(tags=["Logística"])

@router.get("/listar-transportadoras-mais-usadas/")
@handle_error
def listar_transportadoras_mais_usadas(request, offset: int = 10, fetch_next: int = None):
    service = LogisticaService()
    transportadoras, _ = service.listar_transportadoras_mais_usadas(offset=offset, fetch_next=fetch_next)
    return transportadoras
```

**Tratamento de erros na API:**
```python
# core/api/decorators.py
@handle_error  # Decorator que padroniza respostas de erro
```

| Exceção | Status HTTP | Mensagem |
|---------|-------------|----------|
| `ValidationError` | 422 | Erro de validação |
| `DataNotFoundError` | 404 | Dados não encontrados |
| `ServiceError` | 500 | Erro no serviço |

---

## 🟢 Camada de Serviços (Service Layer)

**Localização:** `core/services/`

Esta é a camada central de **regras de negócio** e **transformação de dados**. Utiliza **pandas** para manipulação de dados.

### BaseService

Classe base com funcionalidades comuns:

```python
# core/services/base_service.py
class BaseService:
    """Serviço base com funcionalidades comuns."""
    
    def dataframe_to_list_dicts(self, dataframe: pd.DataFrame) -> List[Dict]:
        """Converte DataFrame para lista de dicionários."""
        
    def list_dicts_to_dataframe(self, data: List[Dict]) -> pd.DataFrame:
        """Converte lista de dicionários para DataFrame."""
        
    def pivot_table(self, data, index, columns, values, aggfunc, fill_value) -> pd.DataFrame:
        """Cria tabela pivô a partir dos dados."""
        
    def replace_column_names_with_month_year(self, dataframe) -> pd.DataFrame:
        """Substitui nomes de colunas no formato 'Mes-Ano' por 'NomeMes-Ano'."""
```

### Services Específicos

**LogisticaService:**
```python
# core/services/logistica_service.py
class LogisticaService(BaseService):
    def __init__(self):
        self.repo = LogisticaRepository()
    
    @handle_service_errors
    @validate_pagination
    def listar_transportadoras_mais_usadas(self, offset: int = 0, fetch_next: int = None):
        data, sql = self.repo.listar_transportadoras_mais_usadas(offset=offset, fetch_next=fetch_next)
        dataframe = self.list_dicts_to_dataframe(data)
        dataframe = self.pivot_table(...)
        # Transformações de dados...
        return data, sql
```

**FinanceiroService:**
```python
# core/services/financeiro_service.py
class FinanceiroService:
    def __init__(self):
        self.repo = FinanceiroRepository()
    
    @handle_service_errors
    def listar_rentabilidade_itens(self, data_inicio: str = None, data_fim: str = None):
        result, sql = self.repo.listar_rentabilidade_itens(data_inicio=data_inicio, data_fim=data_fim)
        return result, sql
```

### Decorators de Serviço

```python
# core/services/decorators.py

@handle_service_errors   # Trata exceções e transforma em erros amigáveis
@validate_pagination     # Valida parâmetros de paginação (offset, fetch_next)
```

### Exceções de Serviço

```python
# core/services/exceptions.py
class ServiceError(Exception):        # Exceção base
class ValidationError(ServiceError):  # Parâmetros inválidos
class BusinessRuleError(ServiceError): # Violação de regra de negócio
class DataNotFoundError(ServiceError): # Dados não encontrados
class DataTransformationError(ServiceError): # Erro ao transformar dados
```

---

## 🟡 Camada de Repositórios (Repository Layer)

**Localização:** `core/repositories/`

Responsável pelo **acesso a dados** e **queries SQL**. Abstrai a comunicação com o banco de dados SQL Server.

### Estrutura

```python
# core/repositories/logistica_repository.py
class LogisticaRepository:
    def __init__(self):
        self.cliente = default_sql_server_client
    
    @handle_db_errors
    def listar_transportadoras_mais_usadas(self, offset: int = 0, fetch_next: int = None):
        sql = f"""
        WITH TransportadorasPaginadas AS (...)
        SELECT ... FROM ... WHERE ...
        """
        return self.cliente.fetch_all(sql), sql
```

```python
# core/repositories/financeiro_repository.py
class FinanceiroRepository:
    def __init__(self):
        self.cliente = default_sql_server_client
    
    @handle_db_errors
    def listar_rentabilidade_itens(self, data_inicio: str = None, data_fim: str = None):
        # Prepara parâmetros de data
        data_inicio_sql, data_fim_sql, _, _ = DateHelper.prepare_date_params(...)
        
        sql = f"""
        DECLARE @DataFim DATE = ...;
        DECLARE @DataInicio DATE = ...;
        
        WITH RENTABILIDADE_ITEM AS (...)
        SELECT ... FROM RENTABILIDADE_ITEM
        """
        return self.cliente.fetch_all(sql), sql
```

### Decorator de Banco de Dados

```python
# core/repositories/decorators.py
@handle_db_errors  # Trata exceções pyodbc e transforma em exceções amigáveis
```

### Exceções de Repositório

```python
# core/repositories/exceptions.py
class RepositoryError(Exception):     # Exceção base
class ConnectionError(RepositoryError): # Erro de conexão
class QueryError(RepositoryError):     # Erro na query SQL
```

---

## 🔴 Camada de Infraestrutura (Infrastructure Layer)

**Localização:** `core/services/`

### Cliente SQL Server

```python
# core/services/sqlserver_cliente.py
class SQLServerCliente:
    def __init__(self, config):
        self.config = config
    
    def connect(self) -> pyodbc.Connection:
        """Estabelece conexão com o banco."""
        
    @contextmanager
    def connection(self):
        """Context manager para conexão (auto-close)."""
        
    def fetch_all(self, query: str, params=None) -> List[Dict]:
        """Executa query e retorna todos os resultados."""
        
    def fetch_one(self, query: str, params=None) -> Dict | None:
        """Executa query e retorna um resultado."""

# Instância padrão
default_sql_server_client = SQLServerCliente(SQLServerConfig())
```

---

## 🛠️ Helpers (Utilitários)

**Localização:** `core/helpers/`

### DateHelper

Utilitário para validação e formatação de datas:

```python
# core/helpers/date_helper.py
class DateHelper:
    DEFAULT_FORMAT = "%Y-%m-%d"
    
    @staticmethod
    def validate_date(date_str: str, param_name: str) -> str:
        """Valida se a string é uma data válida no formato YYYY-MM-DD."""
    
    @staticmethod
    def validate_range(data_inicio: str, data_fim: str) -> tuple[str, str]:
        """Valida um intervalo de datas."""
    
    @staticmethod
    def prepare_date_params(...) -> Tuple[str, str, str, str]:
        """Prepara parâmetros de data para queries SQL."""
```

---

## 🧪 Testes

**Localização:** `core/tests/`

Estrutura de testes espelhando a arquitetura do projeto:

```
core/tests/
├── api/           # Testes de endpoints da API
├── services/      # Testes da camada de serviços
├── repositories/  # Testes da camada de repositórios
└── helpers/       # Testes de utilitários
```

**Framework:** pytest + pytest-django

---

## 🔄 Fluxo de Dados

```
[Cliente/Browser]
        │
        ▼
┌───────────────┐
│   View/API    │ ─── Recebe requisição HTTP
└───────┬───────┘
        │
        ▼
┌───────────────┐
│   Service     │ ─── Aplica regras de negócio e transforma dados
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  Repository   │ ─── Executa queries SQL
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  SQLServer    │ ─── Cliente de conexão com banco
│   Cliente     │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│   Database    │ ─── SQL Server (SAP Business One)
└───────────────┘
```

---

## 📦 Dependências Principais

| Pacote | Versão | Uso |
|--------|--------|-----|
| Django | 5.2.7 | Framework web |
| django-ninja | - | API REST |
| django-allauth | 65.13.0 | Autenticação |
| pandas | 2.3.3 | Manipulação de dados |
| numpy | 2.3.5 | Operações numéricas |
| pyodbc | 5.3.0 | Conexão SQL Server |
| pytest | 9.0.1 | Framework de testes |
| pytest-django | 4.11.1 | Integração pytest + Django |

---

## 🚀 Módulos do Sistema

### Logística
- Listagem de transportadoras mais usadas
- Relação de notas fiscais
- Análise de fretes

### Financeiro
- Rentabilidade de itens
- Análise de faturamento
- Relatórios financeiros

### Dashboard
- Estoque
- Ticket médio
- Consulta de equipamentos e peças

---

## ✅ Boas Práticas Implementadas

1. **Separação de Responsabilidades** - Cada camada tem uma responsabilidade clara
2. **Injeção de Dependências** - Repositórios são injetados nos services
3. **Tratamento de Erros Centralizado** - Decorators para tratamento uniforme
4. **Tipagem** - Uso de type hints para melhor legibilidade
5. **Testes Organizados** - Estrutura de testes espelha a arquitetura
6. **Autenticação** - Views protegidas com LoginRequiredMixin
7. **Documentação Automática** - Django Ninja gera docs da API

---

## 📝 Convenções de Nomenclatura

| Tipo | Convenção | Exemplo |
|------|-----------|---------|
| Classes | PascalCase | `LogisticaService` |
| Métodos | snake_case | `listar_transportadoras_mais_usadas` |
| Variáveis | snake_case | `data_inicio` |
| Constantes | UPPER_SNAKE_CASE | `DEFAULT_FORMAT` |
| Arquivos | snake_case | `logistica_repository.py` |

---

*Documentação gerada em: Janeiro 2026*
