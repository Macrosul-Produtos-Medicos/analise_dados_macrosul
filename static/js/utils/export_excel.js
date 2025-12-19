/**
 * Utilitário para exportar tabelas HTML para Excel/CSV
 * Uso: ExportExcel.toCSV(tableElement, 'nome_arquivo')
 *      ExportExcel.toXLSX(tableElement, 'nome_arquivo') - requer SheetJS
 */

const ExportExcel = {
    /**
     * Exporta uma tabela HTML para CSV
     * @param {HTMLTableElement|string} table - Elemento da tabela ou seletor CSS
     * @param {string} filename - Nome do arquivo (sem extensão)
     * @param {object} options - Opções de exportação
     */
    toCSV(table, filename = 'export', options = {}) {
        const {
            separator = ';',           // Separador de colunas (';' para Excel BR)
            includeHeader = true,      // Incluir cabeçalho
            trimContent = true,        // Remover espaços extras
        } = options;

        const tableEl = typeof table === 'string' ? document.querySelector(table) : table;
        
        if (!tableEl) {
            console.error('ExportExcel: Tabela não encontrada');
            return false;
        }

        const rows = [];

        // Header
        if (includeHeader) {
            const headerRow = tableEl.querySelector('thead tr');
            if (headerRow) {
                const headerData = Array.from(headerRow.querySelectorAll('th, td'))
                    .map(cell => this._formatCell(cell.innerText, trimContent))
                    .join(separator);
                rows.push(headerData);
            }
        }

        // Body
        const bodyRows = tableEl.querySelectorAll('tbody tr');
        bodyRows.forEach(row => {
            const rowData = Array.from(row.querySelectorAll('td, th'))
                .map(cell => this._formatCell(cell.innerText, trimContent))
                .join(separator);
            rows.push(rowData);
        });

        const csvContent = rows.join('\n');
        this._downloadFile(csvContent, `${filename}.csv`, 'text/csv;charset=utf-8;');
        
        return true;
    },

    /**
     * Exporta dados JSON para CSV
     * @param {Array} data - Array de objetos
     * @param {Array} columns - Array com nomes das colunas (opcional)
     * @param {string} filename - Nome do arquivo
     * @param {object} options - Opções de exportação
     */
    fromJSON(data, columns = null, filename = 'export', options = {}) {
        const {
            separator = ';',
            trimContent = true,
        } = options;

        if (!data || data.length === 0) {
            console.error('ExportExcel: Dados vazios');
            return false;
        }

        // Se não passou colunas, usa as chaves do primeiro objeto
        const cols = columns || Object.keys(data[0]);
        
        const rows = [];
        
        // Header
        rows.push(cols.map(col => this._formatCell(col, trimContent)).join(separator));
        
        // Data rows
        data.forEach(item => {
            const rowData = cols
                .map(col => this._formatCell(String(item[col] ?? ''), trimContent))
                .join(separator);
            rows.push(rowData);
        });

        const csvContent = rows.join('\n');
        this._downloadFile(csvContent, `${filename}.csv`, 'text/csv;charset=utf-8;');
        
        return true;
    },

    /**
     * Formata o conteúdo de uma célula para CSV
     */
    _formatCell(content, trim = true) {
        let value = trim ? content.trim() : content;
        // Escapa aspas duplas
        value = value.replace(/"/g, '""');
        // Envolve em aspas se contiver separador, aspas ou quebra de linha
        if (value.includes(';') || value.includes('"') || value.includes('\n')) {
            value = `"${value}"`;
        }
        return `"${value}"`;
    },

    /**
     * Faz o download do arquivo
     */
    _downloadFile(content, filename, mimeType) {
        // BOM para UTF-8 (necessário para Excel reconhecer acentos)
        const BOM = '\uFEFF';
        const blob = new Blob([BOM + content], { type: mimeType });
        
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        
        link.href = url;
        link.download = filename;
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        URL.revokeObjectURL(url);
    }
};

// Disponibiliza globalmente
window.ExportExcel = ExportExcel;
