from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Tuple

class DateHelper:
    """Utilitário para a validação e formatação de datas para SQL"""
    
    DEFAULT_FORMAT = "%Y-%m-%d"
    
    @staticmethod
    def validate_date(date_str: str, param_name: str = "data") -> str:
        """Valida se a string fornecida é uma data válida no formato padrão (YYYY-MM-DD)."""
        
        try:
            parsed_date = datetime.strptime(date_str, DateHelper.DEFAULT_FORMAT)
            return f"{parsed_date.strftime(DateHelper.DEFAULT_FORMAT)}"
        except ValueError:
            raise ValueError(f"A {param_name} '{date_str}' não está no formato válido 'YYYY-MM-DD'.")
    
    
    @staticmethod
    def validate_range(data_inicio: str | None, data_fim: str | None) -> tuple[str, str]:
        """Valida um intervalo de datas e retorna as datas formatadas para SQL."""
        
        data_inicio_sql = DateHelper.validate_date(data_inicio, "data_inicio")
        data_fim_sql = DateHelper.validate_date(data_fim, "data_fim")
        
        if data_inicio_sql > data_fim_sql:
            raise ValueError("A data de início não pode ser maior que a data de fim.")
        
        return data_inicio_sql, data_fim_sql
    
    @staticmethod
    def format_date_for_test(month: int, is_past: bool = True, day : int = None) -> str:
        """Gera uma data formatada para testes, com dia e mês opcionais."""
        
        now = datetime.now()
        
        if is_past:
            target_date = now - relativedelta(months=month)
        else:
            target_date = now + relativedelta(months=month)
            
        if day is not None:
            target_date = target_date.replace(day=day)
            
        return target_date.strftime("%Y-%m-%d")
    
    @staticmethod
    def prepare_date_params(
        data_inicio: str | None,
        data_fim: str | None,
        default_inicio_sql: str = "DATEADD(MONTH, -6, GETDATE())",
        default_fim_sql: str = "GETDATE()",
        default_inicio_months_offset: int = 6,
        defalt_fim_months_offset: int = 0,
        default_inicio_day: int | None = None,
        default_fim_day: int | None = None
    ) -> Tuple[str, str, str, str]:
        """
        Prepara os parâmetros de data para SQL e para testes.
        
        Returns:
            Tuple com:
            - data_inicio_sql: valor para usar na query SQL
            - data_fim_sql: valor para usar na query SQL
            - data_inicio_test: valor string para validação/testes
            - data_fim_test: valor string para validação/testes
        """
        # Preparar valores para teste/validação
        if data_inicio is None:
            data_inicio_sql = default_inicio_sql
            data_inicio_test = DateHelper.format_date_for_test(
                default_inicio_months_offset, 
                is_past=True, 
                day=default_inicio_day
            )
        else:
            data_inicio_sql = f"'{data_inicio}'"
            data_inicio_test = data_inicio
        
        if data_fim is None:
            data_fim_sql = default_fim_sql
            data_fim_test = DateHelper.format_date_for_test(defalt_fim_months_offset, is_past=True, day=default_fim_day)
        else:
            data_fim_sql = f"'{data_fim}'"
            data_fim_test = data_fim
        
        # Validar range
        DateHelper.validate_range(data_inicio_test, data_fim_test)
        
        return data_inicio_sql, data_fim_sql, data_inicio_test, data_fim_test
    

        
        