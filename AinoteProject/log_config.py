import os
from datetime import datetime
import logging
from middleware.current_request import get_current_request

# ログディレクトリ
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# 日付付きファイル名
DATE_FORMAT = datetime.now().strftime("%Y-%m-%d")
LOG_FILE = os.path.join(LOG_DIR, f'app_{DATE_FORMAT}.log')


# カスタムフィルター
class CustomUserFilter(logging.Filter):
    """ログにユーザーIDと名前を追加"""
    def filter(self, record):
        request = get_current_request()
        
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            record.user_id = request.user.id
            record.username = request.user.username
        else:
            record.user_id = 'Anon'
            record.username = 'Anonymous'

        return True


# ログ設定
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    # フォーマット
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} [UID:{user_id}] {module} - {message}',
            'style': '{'
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{'
        },
    },

    # ハンドラー（すべて1ファイルにまとめる）
    'handlers': {
        # コンソール出力
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'filters': ['user_filter']
        },

        # ログファイル（1つに統合）
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_FILE,
            'maxBytes': 5 * 1024 * 1024,   # 5MBでローテート
            'backupCount': 5,               # 5ファイル保持
            'formatter': 'verbose',
            'filters': ['user_filter']
        },
    },

    # フィルター定義
    'filters': {
        'user_filter': {
            '()': CustomUserFilter,
        }
    },

    # ロガー
    'loggers': {
        'django': {                   # Djangoのリクエストログ
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'app': {                       # アプリケーションログ
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'error': {                     # エラーログ
            'handlers': ['file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        }
    }
}
