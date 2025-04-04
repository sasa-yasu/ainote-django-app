import os
from django.shortcuts import render, redirect
from django.conf import settings
from google_auth_oauthlib.flow import Flow
from django.http import HttpResponse, JsonResponse
from .google_calendar import create_event, update_event, delete_event

import logging

# ロガー取得
logger = logging.getLogger('app')
error_logger = logging.getLogger('error')

# Google OAuth 認証のエンドポイント
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def google_login(request):
    flow = Flow.from_client_secrets_file(
        os.path.join(settings.BASE_DIR, 'credentials.json'),
        scopes=SCOPES,
        redirect_uri='http://localhost:8000/oauth2callback'
    )
    
    auth_url, _ = flow.authorization_url(prompt='consent')
    return redirect(auth_url)

def google_callback(request):
    flow = Flow.from_client_secrets_file(
        os.path.join(settings.BASE_DIR, 'credentials.json'),
        scopes=SCOPES,
        redirect_uri='http://localhost:8000/oauth2callback'
    )

    flow.fetch_token(authorization_response=request.build_absolute_uri())

    # 認証トークンを取得
    credentials = flow.credentials
    token_data = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    # トークンを保存する（データベースやセッションに格納可能）
    request.session['google_credentials'] = token_data

    return HttpResponse("Google OAuth 認証が完了しました！")


def create_event_view(request):
    """
    Google カレンダーに新しい予定を登録するビュー
    """
    if 'google_credentials' not in request.session:
        return redirect('google_login')  # 未認証の場合はログインへリダイレクト

    token_data = request.session['google_credentials']

    event_data = {
        'summary': 'テストイベント',
        'location': '東京都渋谷区',
        'description': 'これは Django から登録した Google カレンダーの予定です。',
        'start': {
            'dateTime': '2025-04-05T10:00:00+09:00',
            'timeZone': 'Asia/Tokyo',
        },
        'end': {
            'dateTime': '2025-04-05T11:00:00+09:00',
            'timeZone': 'Asia/Tokyo',
        }
    }

    event = create_event(token_data, event_data)

    return JsonResponse({'message': 'イベントを追加しました', 'event': event})


def update_event_view(request):
    """
    Google カレンダーの予定を更新するビュー
    """
    if 'google_credentials' not in request.session:
        return redirect('google_login')  # 未認証の場合はログインへリダイレクト

    token_data = request.session['google_credentials']
    
    event_id = request.GET.get('event_id')  # 更新するイベントの ID を取得
    if not event_id:
        return JsonResponse({'error': 'event_id が必要です'}, status=400)

    event_data = {
        'summary': '更新されたイベント',
        'location': '東京都新宿区',
        'description': 'これは Django で更新した Google カレンダーの予定です。',
        'start': {
            'dateTime': '2025-04-05T14:00:00+09:00',
            'timeZone': 'Asia/Tokyo',
        },
        'end': {
            'dateTime': '2025-04-05T15:00:00+09:00',
            'timeZone': 'Asia/Tokyo',
        }
    }

    updated_event = update_event(token_data, event_id, event_data)

    return JsonResponse({'message': 'イベントを更新しました', 'event': updated_event})


def delete_event_view(request):
    """
    Google カレンダーの予定を削除するビュー
    """
    if 'google_credentials' not in request.session:
        return redirect('google_login')  # 未認証の場合はログインへリダイレクト

    token_data = request.session['google_credentials']
    
    event_id = request.GET.get('event_id')  # 削除するイベントの ID を取得
    if not event_id:
        return JsonResponse({'error': 'event_id が必要です'}, status=400)

    delete_event(token_data, event_id)

    return JsonResponse({'message': 'イベントを削除しました'})

