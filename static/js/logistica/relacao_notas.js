const RelacaoNotas = () => ({

    notas: [],
    colunas: [],
    offset: 10,
    fetch_next: 10,
    
    // Sorting state
    sortColumn: null,
    sortDirection: 'asc', // 'asc' or 'desc'

    async init(){
        this.notas = await this.fetchNotas(offset=0, fetch_next=10);
        if (this.notas.length > 0) {
            this.colunas = Object.keys(this.notas[0]);
            this.colunas.pop()
            this.colunas.splice(2, 0, 'Total6Meses');
        }
        console.log(this.colunas);
        this.fetchNotas(offset=this.offset).then(data => {
            this.notas = this.notas.concat(data);
            console.log(this.notas);    
        });
    },

    sortBy(coluna) {
        // Toggle direction if same column, otherwise reset to asc
        if (this.sortColumn === coluna) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortColumn = coluna;
            this.sortDirection = 'asc';
        }

        // Sort the data
        this.notas.sort((a, b) => {
            let valA = a[coluna];
            let valB = b[coluna];

            // Handle null/undefined
            if (valA == null) valA = '';
            if (valB == null) valB = '';

            // Numeric comparison
            if (typeof valA === 'number' && typeof valB === 'number') {
                return this.sortDirection === 'asc' ? valA - valB : valB - valA;
            }

            // String comparison
            valA = String(valA).toLowerCase();
            valB = String(valB).toLowerCase();
            
            if (valA < valB) return this.sortDirection === 'asc' ? -1 : 1;
            if (valA > valB) return this.sortDirection === 'asc' ? 1 : -1;
            return 0;
        });
    },

    getSortIcon(coluna) {
        if (this.sortColumn !== coluna) {
            return 'fa-sort'; // Neutral icon
        }
        return this.sortDirection === 'asc' ? 'fa-sort-up' : 'fa-sort-down';
    },

    async fetchNotas(offset=0, fetch_next=null){
        const fetch_next_param = fetch_next !== null ? `&fetch_next=${fetch_next}` : '';
        const response = await fetch(`/api/v1/logistica/listar-transportadoras-mais-usadas/?offset=${offset}${fetch_next_param}`);
        if (response.ok) {
            const data = await response.json();
            return data
        } else {
            console.error('Erro ao buscar notas fiscais');
            return [];
        }
    },

    exportToExcel() {
        if (this.notas.length === 0) {
            alert('Não há dados para exportar');
            return;
        }
        
        // Gera nome do arquivo com data atual
        const today = new Date().toISOString().slice(0, 10);
        const filename = `relacao_notas_${today}`;
        
        // Exporta usando as colunas na ordem correta
        ExportExcel.fromJSON(this.notas, this.colunas, filename);
    },

})