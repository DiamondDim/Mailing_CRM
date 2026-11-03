from django.core.cache import cache


class ClearCacheOnAuthMiddleware:
    """Middleware для очистки кэша при входе/выходе"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Очищаем кэш если это страница входа или выхода
        if request.path in ['/accounts/login/', '/accounts/logout/']:
            cache.delete('/')
            cache.clear()
        return None
