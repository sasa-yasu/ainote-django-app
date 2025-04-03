import threading
from django.utils.deprecation import MiddlewareMixin

# スレッドごとにリクエストを保持
_thread_locals = threading.local()

def get_current_request():
    """現在のリクエストを取得"""
    return getattr(_thread_locals, 'request', None)

class CurrentRequestMiddleware(MiddlewareMixin):
    def process_request(self, request):
        _thread_locals.request = request

