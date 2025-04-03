from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_calendar_service(token_data):
    """
    Google Calendar API に接続するためのサービスオブジェクトを取得
    :param token_data: 認証トークン情報（セッションまたはデータベースから取得）
    :return: Google Calendar API サービスオブジェクト
    """
    credentials = Credentials(
        token=token_data['token'],
        refresh_token=token_data['refresh_token'],
        token_uri=token_data['token_uri'],
        client_id=token_data['client_id'],
        client_secret=token_data['client_secret'],
        scopes=token_data['scopes']
    )
    return build('calendar', 'v3', credentials=credentials)

def create_event(token_data, event_data):
    """
    Google カレンダーに予定を追加する
    :param token_data: 認証トークン情報
    :param event_data: イベント情報（辞書型）
    :return: 作成されたイベント情報
    """
    service = get_calendar_service(token_data)

    event = service.events().insert(
        calendarId='primary',
        body=event_data
    ).execute()

    return event

def update_event(token_data, event_id, event_data):
    """
    Google カレンダーの予定を更新する
    :param token_data: 認証トークン情報
    :param event_id: 更新するイベントの ID
    :param event_data: 更新後のイベント情報（辞書型）
    :return: 更新されたイベント情報
    """
    service = get_calendar_service(token_data)

    event = service.events().update(
        calendarId='primary',
        eventId=event_id,
        body=event_data
    ).execute()

    return event


def delete_event(token_data, event_id):
    """
    Google カレンダーの予定を削除する
    :param token_data: 認証トークン情報
    :param event_id: 削除するイベントの ID
    """
    service = get_calendar_service(token_data)

    service.events().delete(
        calendarId='primary',
        eventId=event_id
    ).execute()
