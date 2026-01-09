const RentabilidadeItens = () => ({
    // Dados
    tabela: [],
    colunas: [],
    offset: 10,

    
    // Ordenação
    sortColumn: null,
    sortDirection: 'asc',
    
    // Filtros
    showFilters: false,
    filtros: {
        campo1: '',
        campo2: '',
    },
    
    // Paginação
    paginaAtual: 1,
    itensPorPagina: 25,
    totalRegistros: 0,
    totalPaginas: 0,

    async init() {
        this.tabela = await this.fetchData();
        if (this.tabela.length > 0) {
            this.colunas = Object.keys(this.tabela[0]);
            this.colunas.pop()
            this.colunas.splice(2, 0, 'Total6Meses');
        }
        this.fetchData(offset=this.offset).then(data => {
            this.tabela = this.tabela.concat(data);   
        });
    },

    async fetchData() {
        // try {
        //     const response = await fetch(`/api/v1/financeiro/rentabilidade-itens?pagina=${this.paginaAtual}&limite=${this.itensPorPagina}`);
        //     const data = await response.json();
        //     this.tabela = data.items;
        //     this.totalRegistros = data.total;
        //     this.totalPaginas = Math.ceil(this.totalRegistros / this.itensPorPagina);
        //     if (this.tabela.length > 0) {
        //         this.colunas = Object.keys(this.tabela[0]);
        //     }
        // } catch (error) {
        //     console.error('Erro ao buscar dados:', error);
        // }
    },

    // Ordenação
    sortBy(coluna) {
        if (this.sortColumn === coluna) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortColumn = coluna;
            this.sortDirection = 'asc';
        }

        this.tabela.sort((a, b) => {
            let valA = a[coluna];
            let valB = b[coluna];

            // Tenta converter para número se possível
            const numA = parseFloat(String(valA).replace(/[^\d.-]/g, ''));
            const numB = parseFloat(String(valB).replace(/[^\d.-]/g, ''));

            if (!isNaN(numA) && !isNaN(numB)) {
                valA = numA;
                valB = numB;
            } else {
                valA = String(valA).toLowerCase();
                valB = String(valB).toLowerCase();
            }

            if (valA < valB) return this.sortDirection === 'asc' ? -1 : 1;
            if (valA > valB) return this.sortDirection === 'asc' ? 1 : -1;
            return 0;
        });
    },

    getSortIcon(coluna) {
        if (this.sortColumn !== coluna) {
            return 'fa-sort';
        }
        return this.sortDirection === 'asc' ? 'fa-sort-up' : 'fa-sort-down';
    },

    // Filtros
    toggleFilters() {
        this.showFilters = !this.showFilters;
    },

    aplicarFiltros() {
        this.paginaAtual = 1;
        this.fetchData();
    },

    limparFiltros() {
        this.filtros = {
            campo1: '',
            campo2: '',
        };
        this.paginaAtual = 1;
        this.fetchData();
    },

    // Paginação
    get paginasVisiveis() {
        const paginas = [];
        const total = this.totalPaginas;
        const atual = this.paginaAtual;
        const delta = 2;

        if (total <= 7) {
            for (let i = 1; i <= total; i++) {
                paginas.push(i);
            }
        } else {
            paginas.push(1);

            if (atual > delta + 2) {
                paginas.push('...');
            }

            const start = Math.max(2, atual - delta);
            const end = Math.min(total - 1, atual + delta);

            for (let i = start; i <= end; i++) {
                paginas.push(i);
            }

            if (atual < total - delta - 1) {
                paginas.push('...');
            }

            paginas.push(total);
        }

        return paginas;
    },

    irParaPagina(pagina) {
        if (pagina >= 1 && pagina <= this.totalPaginas && pagina !== this.paginaAtual) {
            this.paginaAtual = pagina;
            this.fetchData();
        }
    },

    alterarItensPorPagina() {
        this.paginaAtual = 1;
        this.fetchData();
    },

    // Exportar Excel
    exportToExcel() {
        if (this.tabela.length === 0) {
            alert('Não há dados para exportar.');
            return;
        }
        ExportExcel.fromJSON(this.tabela, this.colunas, 'rentabilidade_itens');
    },
});