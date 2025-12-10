from core.services.sqlserver_cliente import default_sql_server_client
from .decorators import handle_db_errors

class LogisticaRepository:
    def __init__(self):
        self.cliente = default_sql_server_client
    
    @handle_db_errors 
    def listar_transportadoras_mais_usadas(self) -> tuple[list[dict], str]:
        sql = """
        SELECT
            T2.CardCode AS CardCode,
            T2.CardName AS CardName,
            
            COUNT(T0.DocEntry) AS Total,
            
            MONTH(T0.DocDate) AS Mes,
            YEAR(T0.DocDate) AS Ano
            
        FROM
            OINV T0
        INNER JOIN
            INV12 T1 ON T0.DocEntry = T1.DocEntry
        INNER JOIN
            OCRD T2 ON T1.Carrier = T2.CardCode
        WHERE
            T0.DocDate >= DATEADD(MONTH, -6, DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()), 0))
        GROUP BY
            T2.CardCode,
            T2.CardName,
            MONTH(T0.DocDate),
            YEAR(T0.DocDate)
        ORDER BY
            CardName, Mes, Ano; """
        return self.cliente.fetch_all(sql), sql