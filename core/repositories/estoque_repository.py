from core.services.sqlserver_cliente import default_sql_server_client
from core.helpers.date_helper import DateHelper

from .decorators import handle_db_errors


class EstoqueRepository:
    def __init__(self):
        self.cliente = default_sql_server_client
    
    @handle_db_errors
    def listar_hits(self):
        sql = """
        DECLARE @DataHoje DATE = GETDATE();
        DECLARE @DataInicio12M DATE = DATEADD(MONTH, -12, DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()), 0));
        DECLARE @DataInicio6M DATE = DATEADD(MONTH, -5, DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()), 0));
        DECLARE @DataInicio30D DATE = DATEADD(DAY, -30, GETDATE()); 

        WITH Pedidos AS (
            SELECT
                RDR1.ItemCode,
                OITM.ItemName,
				OITM.CardCode,
                ORDR.DocEntry,
                ORDR.DocDate,
                CONVERT(VARCHAR(7), ORDR.DocDate, 120) AS AnoMes,
                ORDR.DocStatus
            FROM
                ORDR ORDR
            INNER JOIN
                RDR1 RDR1 ON ORDR.DocEntry = RDR1.DocEntry
            INNER JOIN
                OITM OITM ON OITM.ItemCode = RDR1.ItemCode
            WHERE
                ORDR.DocDate BETWEEN @DataInicio12M AND @DataHoje 
                AND ORDR.CANCELED = 'N'
        )
        SELECT
            A.ItemCode AS ItemCode,
            A.ItemName AS ItemName,
            ISNULL(A.CardCode, '') AS CardCode, 
            
            COUNT(A.DocEntry) AS 'Hits12Meses',

            COUNT(CASE
                WHEN A.DocDate BETWEEN @DataInicio30D AND @DataHoje
                THEN A.DocEntry
            END) AS 'Hits30Dias',

            COUNT(DISTINCT CASE
                WHEN A.DocDate BETWEEN @DataInicio6M AND @DataHoje
                THEN A.AnoMes
            END) AS 'Pedidos06Meses',
            
            (
                SELECT COUNT(DISTINCT CONVERT(VARCHAR(7), T_OINV.DocDate, 120))
                FROM OINV T_OINV
                INNER JOIN INV1 T_INV1 ON T_OINV.DocEntry = T_INV1.DocEntry
                WHERE T_INV1.ItemCode = A.ItemCode
                AND T_OINV.DocDate BETWEEN @DataInicio6M AND @DataHoje
                AND T_OINV.CANCELED = 'N'
            ) AS 'Vendas06Meses'

        FROM
            Pedidos A
        GROUP BY
            A.ItemCode,
            A.ItemName,
            A.CardCode
        ORDER BY
            'Hits12Meses' DESC;
        """
        return self.cliente.fetch_all(sql), sql
    
    @handle_db_errors
    def listar_pedidos_em_transito(self):
        sql = """
        DECLARE @DataInicio DATE =  DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()), 0);
        DECLARE @DataFim DATE = DATEADD(MONTH, 12, DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()), 0));

        SELECT
            POR1.ItemCode AS ItemCode,
            OITM.ItemName AS ItemName, 
                    
            CAST(SUM(POR1.INVQTY) AS INT) AS "INVQTY_Mensal",
            CAST(YEAR(POR1.ShipDate) AS VARCHAR(4)) + '-' + RIGHT('0' + CAST(MONTH(POR1.ShipDate) AS VARCHAR(2)), 2) AS AnoMes

        FROM OPOR OPOR
        INNER JOIN POR1 POR1 ON OPOR.DocEntry = POR1.DocEntry
        INNER JOIN OITM OITM ON POR1.ItemCode = OITM.ItemCode
        WHERE
            POR1.ShipDate BETWEEN @DataInicio AND @DataFim  
            AND OPOR.CANCELED = 'N'

        GROUP BY
            POR1.ItemCode,
            OITM.ItemName,
            CAST(YEAR(POR1.ShipDate) AS VARCHAR(4)) + '-' + RIGHT('0' + CAST(MONTH(POR1.ShipDate) AS VARCHAR(2)), 2)

        ORDER BY
            POR1.ItemCode,
            AnoMes;
        """
        return self.cliente.fetch_all(sql), sql
    
    @handle_db_errors
    def listar_pedidos_de_venda(self, data_inicio: str = None, data_fim: str = None) -> tuple[list[dict], str]:
        
        data_inicio_sql, data_fim_sql, _, _ = DateHelper.prepare_date_params(
            data_inicio,
            data_fim,
            default_inicio_sql="DATEADD(MONTH, -6, DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()), 0))",
            default_fim_sql="GETDATE()",
            default_inicio_months_offset=6,
            default_inicio_day=1
        )
            
        sql = f"""
        DECLARE @DataFim DATE = {data_fim_sql};
        DECLARE @DataInicio DATE = {data_inicio_sql};

        SELECT
            INV1.ItemCode AS ItemCode,
            OITM.ItemName AS ItemName,
            ISNULL(OITM.CardCode, '') AS CardCode, 
            CONVERT(VARCHAR(7), OINV.DocDate, 120) AS AnoMes,
            CONVERT(DECIMAL(19, 1), SUM(INV1.Quantity)) AS QuantidadeVendida
        FROM OINV OINV
        INNER JOIN INV1 INV1 ON OINV.DocEntry = INV1.DocEntry
        INNER JOIN OITM OITM ON INV1.ItemCode = OITM.ItemCode
        WHERE
            OINV.DocDate BETWEEN @DataInicio AND @DataFim 
            AND OINV.CANCELED = 'N'
            AND OITM.ItmsGrpCod IN (101, 102, 103)
            AND OITM.validFor = 'Y'

        GROUP BY
            INV1.ItemCode,
            OITM.ItemName,
            OITM.CardCode,
            CONVERT(VARCHAR(7), OINV.DocDate, 120)
            
        ORDER BY
            INV1.ItemCode,
            CONVERT(VARCHAR(7), OINV.DocDate, 120)
        """
        return self.cliente.fetch_all(sql), sql
    
    @handle_db_errors
    def listar_saida_de_produtos(self, data_inicio: str = None, data_fim: str = None) -> tuple[list[dict], str]:
        
        data_inicio_sql, data_fim_sql, _, _ = DateHelper.prepare_date_params(
            data_inicio,
            data_fim,
            default_inicio_sql="DATEADD(MONTH, -6, GETDATE())",
            default_fim_sql="GETDATE()",
            default_inicio_months_offset=6
        )
        
        sql = f"""
        DECLARE @DataInicio DATE = {data_inicio_sql};
        DECLARE @DataFim DATE = {data_fim_sql};
        WITH PRODUTOS AS (
            SELECT
                OITM.ItemCode,
                OITM.ItemName,
                OCRD.CardCode,
                OCRD.CardName
            FROM OITM
            LEFT JOIN OCRD ON OITM.CardCode = OCRD.CardCode
            WHERE OITM.validFor = 'y'
                AND OITM.ItmsGrpCod IN ('101', '102', '103')
        ),
        MOVIMENTOS AS (
            -- Notas de Saída
            SELECT
                INV1.ItemCode,
                CONVERT(VARCHAR(7), INV1.ActDelDate, 120) AS AnoMes,
                SUM(INV1.InvQty) AS Quantidade
            FROM INV1
            INNER JOIN OINV ON INV1.DocEntry = OINV.DocEntry
            WHERE INV1.ActDelDate BETWEEN @DataInicio AND @DataFim
                AND INV1.Usage IN ('25','21','12','27','34','16','38','15')
                AND INV1.LineStatus = 'O'
                AND OINV.CANCELED = 'N'
            GROUP BY INV1.ItemCode, CONVERT(VARCHAR(7), INV1.ActDelDate, 120)
            
            UNION ALL
            
            -- Notas de Entrada
            SELECT
                DLN1.ItemCode,
                CONVERT(VARCHAR(7), DLN1.ActDelDate, 120),
                SUM(DLN1.InvQty)
            FROM DLN1
            INNER JOIN ODLN ON DLN1.DocEntry = ODLN.DocEntry
            WHERE DLN1.ActDelDate BETWEEN @DataInicio AND @DataFim
                AND DLN1.LineStatus = 'O'
                AND DLN1.Usage IN ('32','1','18','17','25','21','7','12','16')
                AND ODLN.CANCELED = 'N'
            GROUP BY DLN1.ItemCode, CONVERT(VARCHAR(7), DLN1.ActDelDate, 120)
            
            UNION ALL
            
            -- Devolução Entrada (negativo)
            SELECT
                RIN1.ItemCode,
                CONVERT(VARCHAR(7), RIN1.ActDelDate, 120),
                -SUM(RIN1.InvQty)
            FROM RIN1
            INNER JOIN ORIN ON RIN1.DocEntry = ORIN.DocEntry
            WHERE RIN1.ActDelDate BETWEEN @DataInicio AND @DataFim
                AND RIN1.Usage IN ('25','21','12','27','34','16','38','15')
                AND RIN1.LineStatus = 'O'
                AND ORIN.CANCELED = 'N'
            GROUP BY RIN1.ItemCode, CONVERT(VARCHAR(7), RIN1.ActDelDate, 120)
            
            UNION ALL
            
            -- Devolução Entrega (negativo)
            SELECT
                RDN1.ItemCode,
                CONVERT(VARCHAR(7), RDN1.ActDelDate, 120),
                -SUM(RDN1.InvQty)
            FROM RDN1
            INNER JOIN ORDN ON RDN1.DocEntry = ORDN.DocEntry
            WHERE RDN1.ActDelDate BETWEEN @DataInicio AND @DataFim
                AND RDN1.LineStatus = 'O'
                AND RDN1.Usage IN ('32','1','18','17','25','21','7','12','16')
                AND ORDN.CANCELED = 'N'
            GROUP BY RDN1.ItemCode, CONVERT(VARCHAR(7), RDN1.ActDelDate, 120)
        )
        SELECT
            P.ItemCode,
            P.ItemName,
            P.CardCode,
            P.CardName,
            M.AnoMes,
            ISNULL(SUM(M.Quantidade), 0) AS Total
        FROM PRODUTOS P
        LEFT JOIN MOVIMENTOS M ON P.ItemCode = M.ItemCode
        GROUP BY P.ItemCode, P.ItemName, P.CardCode, P.CardName, M.AnoMes
        HAVING M.AnoMes IS NOT NULL OR SUM(M.Quantidade) IS NULL
        ORDER BY P.ItemCode, M.AnoMes;
        """
        return self.cliente.fetch_all(sql), sql


