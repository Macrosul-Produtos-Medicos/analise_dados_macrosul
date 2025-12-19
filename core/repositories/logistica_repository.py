from core.services.sqlserver_cliente import default_sql_server_client
from .decorators import handle_db_errors

class LogisticaRepository:
    def __init__(self):
        self.cliente = default_sql_server_client
    
    @handle_db_errors 
    def listar_transportadoras_mais_usadas(self, offset: int = 0, fetch_next: int = None) -> tuple[list[dict], str]:
        """
        Lista as transportadoras mais usadas com paginação por transportadora (não por linha).
        
        A paginação é feita primeiro nas transportadoras únicas, depois busca todos os dados
        dessas transportadoras (todos os meses/anos).
        """
        # Monta a paginação da CTE
        pagination = f"OFFSET {offset} ROWS"
        if fetch_next is not None:
            pagination += f" FETCH NEXT {fetch_next} ROWS ONLY"
        
        sql = f"""
        WITH TransportadorasPaginadas AS (
            -- Primeiro: paginar as transportadoras únicas
            SELECT DISTINCT
                OCRD.CardCode,
                OCRD.CardName
            FROM OINV OINV
            INNER JOIN INV12 INV12 ON OINV.DocEntry = INV12.DocEntry
            INNER JOIN OCRD OCRD ON INV12.Carrier = OCRD.CardCode
            WHERE OINV.DocDate >= DATEADD(MONTH, -6, DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()), 0))
            ORDER BY OCRD.CardName
            {pagination}
        )
        -- Depois: buscar TODOS os dados dessas transportadoras (todos os meses)
        SELECT
            OCRD.CardCode AS CardCode,
            OCRD.CardName AS CardName,
            COUNT(OINV.DocEntry) AS Total,
            MONTH(OINV.DocDate) AS Mes,
            YEAR(OINV.DocDate) AS Ano
        FROM OINV OINV
        INNER JOIN INV12 INV12 ON OINV.DocEntry = INV12.DocEntry
        INNER JOIN OCRD OCRD ON INV12.Carrier = OCRD.CardCode
        WHERE 
            OCRD.CardCode IN (SELECT CardCode FROM TransportadorasPaginadas)
            AND OINV.DocDate >= DATEADD(MONTH, -6, DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()), 0))
        GROUP BY
            OCRD.CardCode,
            OCRD.CardName,
            MONTH(OINV.DocDate),
            YEAR(OINV.DocDate)
        ORDER BY
            OCRD.CardName, Mes, Ano
        """
            
        return self.cliente.fetch_all(sql), sql
    
    @handle_db_errors
    def contar_transportadoras(self) -> tuple[int, str]:
        """Retorna o total de transportadoras únicas para calcular paginação."""
        sql = """
        SELECT COUNT(DISTINCT T2.CardCode) AS Total
        FROM OINV T0
        INNER JOIN INV12 T1 ON T0.DocEntry = T1.DocEntry
        INNER JOIN OCRD T2 ON T1.Carrier = T2.CardCode
        WHERE T0.DocDate >= DATEADD(MONTH, -6, DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()), 0))
        """
        result = self.cliente.fetch_one(sql)
        return result["Total"] if result else 0, sql