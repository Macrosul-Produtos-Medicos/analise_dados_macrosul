from core.services.sqlserver_cliente import default_sql_server_client

from core.helpers.date_helper import DateHelper
from .decorators import handle_db_errors

class FinanceiroRepository:
    def __init__(self):
        self.cliente = default_sql_server_client

    @handle_db_errors
    def listar_rentabilidade_itens(self, data_inicio: str | None = None, data_fim: str | None = None) -> tuple[list[dict], str]:
        
        data_inicio_sql, data_fim_sql, _, _ = DateHelper.prepare_date_params(
            data_inicio,
            data_fim,
            default_inicio_sql="DATEADD(MONTH, -12, GETDATE())",
            default_fim_sql="GETDATE()",
            default_inicio_months_offset=12,
            default_inicio_day=1
        )
        
        sql = f"""
        DECLARE @DataFim DATE = {data_fim_sql};
        DECLARE @DataInicio DATE = {data_inicio_sql};

        WITH RENTABILIDADE_ITEM AS (
            SELECT
                INV1.ItemCode,
                OITM.ItemName,
                OCDR.U_Tipo_Negocios,
                CAST(SUM(INV1.Quantity) AS int) as 'Quantidade',
                ITM1.Price,
                SUM(ITM1.Price * INV1.Quantity) AS 'PrecoMinimo',
                SUM(INV1.LineTotal + INV1.VatSum) AS 'PrecoFaturado',
                SUM(INV1.LineTotal + INV1.VatSum) AS 'FaturamentoPorItem',
                (SUM(INV1.LineTotal + INV1.VatSum) - SUM((ITM1.Price * INV1.Quantity))) / (SUM((ITM1.Price * INV1.Quantity))) * 100 as  'Rentabilidade'
            FROM OINV OINV
            INNER JOIN INV1 INV1 ON OINV.DocEntry = INV1.DocEntry
            INNER JOIN OITM OITM ON INV1.ItemCode = OITM.ItemCode
            INNER JOIN OCRD OCDR ON OCDR.CardCode = OINV.CardCode
            INNER JOIN ITM1 ITM1 on ITM1.PriceList = 4 and OITM.ItemCode = ITM1.ItemCode
            WHERE
                OINV.TaxDate BETWEEN @DataInicio AND @DataFim 
                AND OINV.CANCELED = 'N' 
                AND OINV.ObjType = 13

            GROUP BY 
                INV1.ItemCode,
                OITM.ItemName,
                OCDR.U_Tipo_Negocios,
                ITM1.Price
        
            UNION ALL

            SELECT
                RIN1.ItemCode,
                OITM.ItemName,
                OCDR.U_Tipo_Negocios,
                -CAST(SUM(RIN1.Quantity) AS int) as 'Quantidade',
                ITM1.Price,
                -SUM(ITM1.Price * RIN1.Quantity) AS 'PrecoMinimo',
                -SUM(RIN1.LineTotal + RIN1.VatSum) AS 'PrecoFaturado',
                -SUM(RIN1.LineTotal + RIN1.VatSum) AS 'FaturamentoPorItem',
                -(SUM(RIN1.LineTotal + RIN1.VatSum) - SUM((ITM1.Price * RIN1.Quantity))) / (SUM((ITM1.Price * RIN1.Quantity))) * 100 as  'Rentabilidade'
            FROM ORIN ORIN
            INNER JOIN RIN1 RIN1 ON ORIN.DocEntry = RIN1.DocEntry
            INNER JOIN OITM OITM ON RIN1.ItemCode = OITM.ItemCode
            INNER JOIN OCRD OCRD ON OCRD.CardCode = ORIN.CardCode
            INNER JOIN ITM1 ITM1 on ITM1.PriceList = 4 and OITM.ItemCode = ITM1.ItemCode

            WHERE
                ORIN.TaxDate BETWEEN @DataInicio AND @DataFim
                AND ORIN.CANCELED = 'N'
                AND ORIN.ObjType = 14

            GROUP BY
                RIN1.ItemCode,
                OITM.ItemName,
                OCRD.U_Tipo_Negocios,
                ITM1.Price
        )
        SELECT
            A.ItemCode,
            A.ItemName,
            A.U_Tipo_Negocios AS 'TipoDoNegocio',
            CONVERT(DECIMAL(19, 0), SUM(A.Quantidade)) AS 'Quantidade',
            CONVERT(DECIMAL(19, 2), A.Price) AS 'PrecoMinimoUnitario',
            CONVERT(DECIMAL(19, 2), SUM(A.FaturamentoPorItem)) AS 'FaturamentoPorItem',
            CONVERT(DECIMAL(19, 2), SUM(A.Rentabilidade)) AS 'Rentabilidade'
        FROM RENTABILIDADE_ITEM A

        GROUP BY
            A.ItemCode,
            A.ItemName,
            A.U_Tipo_Negocios,
            A.Price
        ORDER BY
            A.ItemCode,
            'TipoDoNegocio' ASC
        """
        return self.cliente.fetch_all(sql), sql