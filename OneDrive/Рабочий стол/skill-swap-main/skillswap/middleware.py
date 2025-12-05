"""
Custom middleware for monitoring and logging
"""
import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('accounts')


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware для логирования всех запросов и времени их выполнения
    """
    
    def process_request(self, request):
        request.start_time = time.time()
        return None
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Логируем только медленные запросы (> 1 секунды) или ошибки
            if duration > 1.0 or response.status_code >= 400:
                logger.warning(
                    f'{request.method} {request.path} - '
                    f'Status: {response.status_code} - '
                    f'Duration: {duration:.2f}s - '
                    f'User: {getattr(request.user, "username", "Anonymous")}'
                )
        
        return response

