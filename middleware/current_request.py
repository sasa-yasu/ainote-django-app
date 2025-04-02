import threading

# スレッドごとにリクエストを保持
_thread_locals = threading.local()

def get_current_request():
    """現在のリクエストを取得"""
    return getattr(_thread_locals, 'request', None)

class ThreadLocalMiddleware:
    """リクエストをスレッドローカルに保持するミドルウェア"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # スレッドごとにリクエストを保持
        _thread_locals.request = request
        response = self.get_response(request)
        return response
