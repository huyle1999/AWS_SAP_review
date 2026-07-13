# LittleLemonAPI/middleware.py
import uuid
import logging
from django.core.cache import cache
from django.http import JsonResponse

logger = logging.getLogger(__name__)

class ObservabilityMiddleware:
    """
    Gắn Request-ID cho OTEL tracing + Idempotency cho write operations.
    Thread-safe nhờ Django cache backend (Redis/LocMem đều atomic).
    """
    IDEMPOTENT_METHODS = {'POST', 'PUT', 'PATCH'}
    CACHE_PREFIX = 'idempotency:'
    TTL = 3600  # 1 giờ

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Gán Request-ID (bắt buộc cho OTEL trace correlation)
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        request.request_id = request_id
        
        # 2. Idempotency check cho write methods
        if request.method in self.IDEMPOTENT_METHODS:
            idem_key = request.headers.get('Idempotency-Key')
            if idem_key:
                cache_key = f"{self.CACHE_PREFIX}{idem_key}"
                # add() là atomic operation → thread-safe, chống race condition
                acquired = cache.add(cache_key, 'processing', self.TTL)
                
                if not acquired:
                    cached = cache.get(cache_key)
                    if cached == 'processing':
                        return JsonResponse(
                            {"error": "Request is being processed"}, 
                            status=409
                        )
                    else:
                        # Trả về response đã cache (idempotent replay)
                        return JsonResponse(cached['body'], status=cached['status'])
                
                # Đánh dấu request này cần cache response sau khi xử lý xong
                request.idempotency_cache_key = cache_key

        response = self.get_response(request)
        
        # 3. Cache response cho idempotency (nếu có key)
        if hasattr(request, 'idempotency_cache_key'):
            cache.set(request.idempotency_cache_key, {
                'body': response.data if hasattr(response, 'data') else {},
                'status': response.status_code
            }, self.TTL)
        
        # 4. Gắn Request-ID vào response header (cho client + OTEL collector)
        response['X-Request-ID'] = request_id
        return response