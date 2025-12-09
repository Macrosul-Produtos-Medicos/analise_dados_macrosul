from core.services.sqlserver_cliente import default_sql_server_client
from .decorators import handle_db_errors

class DashboardRepository:
    def __init__(self):
        self.cliente = default_sql_server_client
        
    
    @handle_db_errors 
    def listar_notas_fiscais(self, ano : int = None) -> tuple[list[dict], str]:

        sql = """
            SELECT
                COUNT(distinct(OINV.Serial)) AS quantidade_notas,
                ,CAST(SUM(INV1.Quantity) AS int) as quantidade_itens,
                ,OINV.DocDate as data_emissao
                ,DATEPART(MONTH, OINV.DocDate) as mes_emissao
                ,DATEPART(WEEK, OINV.DocDate) as semana_emissao
                ,DATEPART(YEAR, OINV.DocDate) as ano_emissao
            FROM OINV OINV
            JOIN INV1 INV1 ON OINV.DocEntry = INV1.DocEntry
            WHERE 
                OINV.CANCELED = 'N'
                AND OINV.InvntSttus = 'O'
            GROUP BY
                OINV.DocDate
            ORDER BY
                OINV.DocDate
        """
        parameters = []
        if ano is not None:
            sql += " AND YEAR(OINV.DocDate) = ?"
            parameters.append(ano)
            
        return self.cliente.fetch_all(sql, parameters), sql
