import pytest
from core.helpers.date_helper import DateHelper

def test_date_helper_instantiation():
    date_helper = DateHelper()
    assert date_helper is not None
    assert isinstance(date_helper, DateHelper)
    
def test_validate_date_valid():
    valid_date_str = "2024-06-15"
    result = DateHelper.validate_date(valid_date_str)
    assert result == "2024-06-15"

def test_validate_date_invalid():
    invalid_date_str = "15-06-2024"
    with pytest.raises(ValueError) as exc_info:
        DateHelper.validate_date(invalid_date_str)
    assert str(exc_info.value) == "A data '15-06-2024' não está no formato válido 'YYYY-MM-DD'."

def test_validate_range():
    
    data_inicio: str = "2024-01-01"
    data_fim: str = "2024-12-31"
    
    data_inicio_sql, data_fim_sql = DateHelper.validate_range(data_inicio, data_fim)
    assert data_inicio_sql == "2024-01-01"
    assert data_fim_sql == "2024-12-31"

def test_validate_range_invalid():
    data_inicio: str = "2024-01-32"  # Invalid day
    data_fim: str = "2024-12-31"
    
    with pytest.raises(ValueError) as exc_info:
        DateHelper.validate_range(data_inicio, data_fim)
        
def test_validate_range_inicio_greater_fim():
    data_inicio: str = "2024-12-31"
    data_fim: str = "2024-01-01"
    
    with pytest.raises(ValueError) as exc_info:
        DateHelper.validate_range(data_inicio, data_fim)

def test_format_date_for_test_past():
    month = 3
    day = 15
    result = DateHelper.format_date_for_test(month, is_past=True, day=day)
    
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    
    expected_date = datetime.now() - relativedelta(months=month)
    expected_date = expected_date.replace(day=day)
    expected_str = expected_date.strftime("%Y-%m-%d")
    
    assert result == expected_str

def test_format_date_for_test_future():
    month = 2
    day = 10
    result = DateHelper.format_date_for_test(month, is_past=False, day=day)
    
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    
    expected_date = datetime.now() + relativedelta(months=month)
    expected_date = expected_date.replace(day=day)
    expected_str = expected_date.strftime("%Y-%m-%d")
    
    assert result == expected_str
    
def test_format_date_for_test_no_day():
    month = 5
    result = DateHelper.format_date_for_test(month, is_past=True)
    
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    
    expected_date = datetime.now() - relativedelta(months=month)
    expected_str = expected_date.strftime("%Y-%m-%d")
    
    assert result == expected_str

def test_format_date_for_test_today():
    month = 0
    result = DateHelper.format_date_for_test(month, is_past=True)
    
    from datetime import datetime
    
    expected_date = datetime.now()
    expected_str = expected_date.strftime("%Y-%m-%d")
    
    assert result == expected_str
    
def test_prepare_date_params_all_none():
    data_inicio = None
    data_fim = None
    
    data_inicio_sql, data_fim_sql, data_inicio_test, data_fim_test = DateHelper.prepare_date_params(data_inicio, data_fim)
    
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    
    expected_inicio_test = (datetime.now() - relativedelta(months=6)).strftime("%Y-%m-%d")
    expected_fim_test = datetime.now().strftime("%Y-%m-%d")
    
    assert data_inicio_sql == "DATEADD(MONTH, -6, GETDATE())"
    assert data_fim_sql == "GETDATE()"
    assert data_inicio_test == expected_inicio_test
    assert data_fim_test == expected_fim_test
    
def test_prepare_date_params_with_values():
    data_inicio = "2024-01-01"
    data_fim = "2024-06-30"
    
    data_inicio_sql, data_fim_sql, data_inicio_test, data_fim_test = DateHelper.prepare_date_params(data_inicio, data_fim)
    
    assert data_inicio_sql == "'2024-01-01'"
    assert data_fim_sql == "'2024-06-30'"
    assert data_inicio_test == "2024-01-01"
    assert data_fim_test == "2024-06-30"
    
def test_prepare_date_params_partial_none():
    data_inicio = None
    data_fim = "2025-12-31"
    
    data_inicio_sql, data_fim_sql, data_inicio_test, data_fim_test = DateHelper.prepare_date_params(data_inicio, data_fim)
    
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    
    expected_inicio_test = (datetime.now() - relativedelta(months=6)).strftime("%Y-%m-%d")
    
    assert data_inicio_sql == "DATEADD(MONTH, -6, GETDATE())"
    assert data_fim_sql == "'2025-12-31'"
    assert data_inicio_test == expected_inicio_test
    assert data_fim_test == "2025-12-31"

def test_prepare_date_params_default_day():
    data_inicio = None
    data_fim = None
    
    data_inicio_sql, data_fim_sql, data_inicio_test, data_fim_test = DateHelper.prepare_date_params(
        data_inicio, 
        data_fim, 
        default_inicio_day=10
    )
    
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    
    expected_inicio_date = datetime.now() - relativedelta(months=6)
    expected_inicio_date = expected_inicio_date.replace(day=10)
    expected_inicio_test = expected_inicio_date.strftime("%Y-%m-%d")
    
    expected_fim_test = datetime.now().strftime("%Y-%m-%d")
    
    assert data_inicio_sql == "DATEADD(MONTH, -6, GETDATE())"
    assert data_fim_sql == "GETDATE()"
    assert data_inicio_test == expected_inicio_test
    assert data_fim_test == expected_fim_test

@pytest.mark.django_db
def test_prepare_date_params_default_inicio_sql():
    data_inicio = None
    data_fim = None
    
    custom_default_inicio_sql = "DATEADD(YEAR, -1, GETDATE())"
    
    data_inicio_sql, data_fim_sql, data_inicio_test, data_fim_test = DateHelper.prepare_date_params(
        data_inicio, 
        data_fim, 
        default_inicio_sql=custom_default_inicio_sql,
        default_inicio_months_offset=12
    )
    
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    
    expected_inicio_test = (datetime.now() - relativedelta(years=1)).strftime("%Y-%m-%d")
    expected_fim_test = datetime.now().strftime("%Y-%m-%d")
    
    assert data_inicio_sql == custom_default_inicio_sql
    assert data_fim_sql == "GETDATE()"
    assert data_inicio_test == expected_inicio_test
    assert data_fim_test == expected_fim_test

@pytest.mark.django_db
def test_prepare_date_params_default_fim_sql():
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    
    data_inicio = None
    data_fim = None
    
    custom_default_fim_sql = "DATEADD(DAY, -1, GETDATE())"
    
    data_inicio_sql, data_fim_sql, data_inicio_test, data_fim_test = DateHelper.prepare_date_params(
        data_inicio, 
        data_fim, 
        default_fim_sql=custom_default_fim_sql,
        defalt_fim_months_offset=0,
        default_fim_day=datetime.now().day - 1
    )
    
    
    expected_inicio_test = (datetime.now() - relativedelta(months=6)).strftime("%Y-%m-%d")
    expected_fim_test = (datetime.now() - relativedelta(days=1)).strftime("%Y-%m-%d")
    
    assert data_inicio_sql == "DATEADD(MONTH, -6, GETDATE())"
    assert data_fim_sql == custom_default_fim_sql
    assert data_inicio_test == expected_inicio_test
    assert data_fim_test == expected_fim_test
    


@pytest.mark.django_db
def test_prepare_date_params_invalid_range():
    data_inicio = "2024-12-31"
    data_fim = "2024-01-01"
    
    with pytest.raises(ValueError) as exc_info:
        DateHelper.prepare_date_params(data_inicio, data_fim)
        
def test_prepare_date_params_invalid_date():
    data_inicio = "2024-13-01"  # Invalid month
    data_fim = "2024-06-30"
    
    with pytest.raises(ValueError) as exc_info:
        DateHelper.prepare_date_params(data_inicio, data_fim)
        
