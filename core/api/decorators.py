from core.services.exceptions import (
    ServiceError,
    ValidationError,
    BusinessRuleError,
    DataNotFoundError,
    DataTransformationError,
)

from http import HTTPStatus
from django.conf import settings
import logging
from functools import wraps
from django.http import JsonResponse

logger = logging.getLogger(__name__)

class ErrorMessages:
    VALIDATION_ERROR = "Erro de validação"
    NOT_FOUND = "Recurso não encontrado"
    INTERNAL_ERROR = "Erro interno do servidor"
    SERVICE_ERROR = "Erro no serviço"
    DATA_TRANSFORMATION_ERROR = "Erro na transformação de dados"
    BUSINESS_RULE_ERROR = "Erro de regra de negócio"
    DATA_NOT_FOUND_ERROR = "Dados não encontrados"
    
    

def handle_error(func):
    """
    Decorator para padronizar o tratamento de erros nas views da API.

    Este decorator captura exceções comuns e retorna respostas JSON padronizadas:
    - ValueError: Retorna status 400 com mensagem de parâmetros inválidos
    - FileNotFoundError: Retorna status 404 com mensagem de recurso não encontrado
    - Exception geral: Retorna status 500 com mensagem de erro interno

    Args:
        func: Função da view a ser decorada

    Returns:
        JsonResponse: Resposta JSON padronizada em caso de erro
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            logger.warning(f'Erro de validação em {func.__name__}: {str(e)}')
            return JsonResponse(
                {'error': True, 'message': ErrorMessages.VALIDATION_ERROR, 'details': str(e)},
                status=HTTPStatus.UNPROCESSABLE_ENTITY,
            )
        except DataNotFoundError as e:
            logger.warning(f'Recurso não encontrado em {func.__name__}: {str(e)}')
            return JsonResponse(
                {'error': True, 'message': ErrorMessages.DATA_NOT_FOUND_ERROR, 'details': str(e)}, 
                status=HTTPStatus.NOT_FOUND
            )
            
        except BusinessRuleError as e:
            logger.warning(f'Erro de regra de negócio em {func.__name__}: {str(e)}')
            return JsonResponse(
                {'error': True, 'message': ErrorMessages.BUSINESS_RULE_ERROR, 'details': str(e)},
                status=HTTPStatus.BAD_REQUEST,
            )
        
        except DataTransformationError as e:
            logger.error(f'Erro de transformação de dados em {func.__name__}: {str(e)}', exc_info=True)
            return JsonResponse(
                {'error': True, 'message': ErrorMessages.DATA_TRANSFORMATION_ERROR, 'details': str(e)},
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
            
        except ServiceError as e:
            logger.error(f'Erro de serviço em {func.__name__}: {str(e)}', exc_info=True)
            return JsonResponse(
                {'error': True, 'message': ErrorMessages.SERVICE_ERROR, 'details': str(e)},
                status=HTTPStatus.SERVICE_UNAVAILABLE,
            )
        
        except Exception as e:
            logger.error(f'Erro interno em {func.__name__}: {str(e)}', exc_info=True)
            return JsonResponse(
                {
                    'error': True,
                    'message': ErrorMessages.INTERNAL_ERROR,
                    'details': str(e) if settings.DEBUG else 'Erro interno',
                },
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

    return wrapper