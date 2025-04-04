import os
from django.utils.timezone import now
import math
from PIL import Image
from io import BytesIO
import qrcode
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponse

import logging

# ロガー取得
logger = logging.getLogger('app')
error_logger = logging.getLogger('error')

# 画像ハンドリング系[images]
def create_images(object, images_data):
    ext = os.path.splitext(images_data.name)[1]  # 拡張子を取得
    timestamp = now().strftime('%y%m%d%H%M')  # タイムスタンプ生成 (yyMMddHHmm)
    images_data.name = f"{object.id}_images_{timestamp}{ext}"  # 例: "12_2503201935.jpg"
    logger.debug(f'new images_data={images_data}')

    return images_data

def delete_images(object):
    old_image_path = object.images.path  # 旧ファイルのパス
    logger.debug(f'old images_data={old_image_path}')
    if default_storage.exists(old_image_path):
        logger.debug('old images_data file exists')
        try:
            logger.debug('delete old images_data')
            default_storage.delete(old_image_path)  # 削除
        except Exception as e:
            logger.debug(f'couldnt delete old images_data={old_image_path}: {e}')
    else:
        logger.debug('old images_data file not exists')

    return object

def update_images(object, images_data):
    if object.images:
        logger.debug('old images_data exists')
        # **古いファイルを削除**
        delete_images(object)

    # **新しいファイルを保存**
    images_data = create_images(object, images_data)

    return images_data

# 画像ハンドリング系[themes]
def create_themes(object, themes_data):
    ext = os.path.splitext(themes_data.name)[1]  # 拡張子を取得
    timestamp = now().strftime('%y%m%d%H%M')  # タイムスタンプ生成 (yyMMddHHmm)
    themes_data.name = f"{object.id}_themes_{timestamp}{ext}"  # 例: "12_2503201935.jpg"
    logger.debug(f'themes_data={themes_data}')

    return themes_data

def delete_themes(object):
    old_image_path = object.themes.path  # 旧ファイルのパス
    logger.debug(f'old themes_data={old_image_path}')
    if default_storage.exists(old_image_path):
        logger.debug('old themes_data file exists')
        try:
            logger.debug('delete old themes_data')
            default_storage.delete(old_image_path)  # 削除
        except Exception as e:
            logger.error(f'couldnt delete old themes_data={old_image_path}: {e}')
    else:
        logger.debug('old themes_data file not exists')

    return object

def update_themes(object, themes_data):
    if object.themes:
        logger.debug('old themes_data exists')
        # **古いファイルを削除**
        delete_themes(object)

    # **新しいファイルを保存**
    themes_data = create_themes(object, themes_data)

    return themes_data

# 画像サイズ調整系
def resize_image(p_images, p_size):
    """
    長辺が指定サイズになるように画像をリサイズ
    """
    img = Image.open(p_images)
    format = img.format if img.format else "JPEG"  # フォーマットがない場合はJPEG

    # 画像の長辺・短辺を判定
    width, height = img.size
    if width >= height:
        # 横長 → 幅が長辺
        new_width = p_size
        new_height = int((height / width) * p_size)
    else:
        # 縦長 → 高さが長辺
        new_height = p_size
        new_width = int((width / height) * p_size)

    # アスペクト比を維持したまま長辺を指定サイズにリサイズ
    img = img.resize((new_width, new_height), Image.LANCZOS)  # 高品質リサイズ

    # バッファに保存
    img_io = BytesIO()
    img.save(img_io, format=format)

    # imagesを更新
    p_images = ContentFile(img_io.getvalue(), name=p_images.name)

    return p_images


def crop_square_image(p_images, p_size):
    img = Image.open(p_images)
    format = img.format if img.format else "JPEG" # フォーマットがない場合はJPEGで保存

    # 短辺を基準に正方形で切り取る
    min_side = min(img.size)  # 短辺の長さ
    left = (img.width - min_side) / 2
    top = (img.height - min_side) / 2
    right = (img.width + min_side) / 2
    bottom = (img.height + min_side) / 2
    img = img.crop((left, top, right, bottom))  # 正方形にトリミング
    print('p_images img.crop')

    img.resize((p_size, p_size), Image.LANCZOS)  # 高品質なリサイズ

    img_io = BytesIO() # prepare buffer area
    print(f'p_images img.format={img.format}')
    img.save(img_io, format=format) # save to buffer area

    p_images = ContentFile(img_io.getvalue(), name=p_images.name) # Update the images size

    return p_images


def crop_16_9_image(p_themes, p_size):
    img = Image.open(p_themes)
    format = img.format if img.format else "JPEG" # フォーマットがない場合はJPEGで保存

    # アスペクト比 16:9 にトリミング
    img_width, img_height = img.size
    target_ratio = 16 / 9

    # 現在のアスペクト比を計算
    current_ratio = img_width / img_height

    if current_ratio > target_ratio:
        # 幅が長すぎる場合 → 幅を切り取る
        new_width = int(img_height * target_ratio)
        left = (img_width - new_width) / 2
        top = 0
        right = (img_width + new_width) / 2
        bottom = img_height
    else:
        # 高さが長すぎる場合 → 高さを切り取る
        new_height = int(img_width / target_ratio)
        left = 0
        top = (img_height - new_height) / 2
        right = img_width
        bottom = (img_height + new_height) / 2

    # トリミング
    img = img.crop((left, top, right, bottom))
    print('p_themes img.crop')

    new_height = int((img.height / img.width) * p_size)
    img = img.resize((p_size, new_height), Image.LANCZOS)

    img_io = BytesIO() # prepare buffer area
    print(f'p_themes img.format={img.format}')
    img.save(img_io, format=format) # save to buffer area

    p_themes = ContentFile(img_io.getvalue(), name=p_themes.name) # Update the themes size
    
    return p_themes


# GPS座標系
def haversine(lat1, lon1, lat2, lon2):
    """2点間のハーサイン距離から近くにいるかを判断"""
    R = 6371  # 地球の半径（キロメートル）
    tolerance = 1.0  # 0.3=300メートル範囲

    # 緯度経度をラジアンに変換
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # 緯度と経度の差を計算
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # ハーサイン公式を適用
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # 距離を返す
    distance = R * c
    logger.debug(f'distance={distance}')
    logger.debug(f'tolerance={tolerance}')

    if distance < tolerance:
        return True
    else:
        return False

# QRコード系
def disp_qr_code(url_for_qr):

    qr = qrcode.QRCode(
        version=4,  # サイズ (1～40, 数字が大きいほどサイズが大きい)
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # エラーレベル
        box_size=10,  # 1セルあたりのピクセルサイズ
        border=6,  # ボーダーサイズ
    )
    
    qr.add_data(url_for_qr) # create QR code
    qr.make(fit=True)

    # QRコード生成
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    logo_path = f"{settings.BASE_DIR}/static/img/ainote.png"

    try:
        logger.debug(f"Logo file load from: {logo_path}")
        logo = Image.open(logo_path)

        logo_size = (128, 128)
        logo = logo.resize(logo_size) #  ロゴサイズ変更

        pos = (
            (qr_img.size[0] - logo.size[0]) // 2,
            (qr_img.size[1] - logo.size[1]) // 2
        )

        qr_img.paste(logo, pos) # QRコード中央にロゴを貼り付け

    except Exception as e:
        logger.error(f"Failed to load logo: {e}")

    img_io = BytesIO() # save QR code as binary image data
    qr_img.save(img_io, format='PNG') # ext is PNG
    img_io.seek(0)

    return HttpResponse(img_io.getvalue(), content_type="image/png")

# MBTI系
import pandas as pd

# MBTI相性データを辞書として定義（もしくはDBから取得）
mbti_matrix = {
    "INTJ": {
        "ESFJ": {"pt": 5, "relation": "opposite", "description": "表裏一体な最高の相性◎"},
        "ISFP": {"pt": 4, "relation": "active", "description": "居心地が良く気持ちがプラスになる"},
        "ENTP": {"pt": 3, "relation": "mirror", "description": "心理は似てて態度が違う双子みたい"},
        "INFJ": {"pt": 3, "relation": "similler", "description": "ビジネスライクな似た者同士"},
        "ENFJ": {"pt": 2, "relation": "opposite_sub", "description": "惹かれ合いゆっくり距離が縮まる"},
        "ESTJ": {"pt": 2, "relation": "relax", "description": "ダラダラ快適で温かく安定感あり"},
        "INTJ": {"pt": 1, "relation": "same", "description": "理解し合えるが助け合いが難しい"},
        "INTP": {"pt": 1, "relation": "same_sub", "description": "似てるようで似てない波ある関係"},
    },
    "INTP": {
        "ESFP": {"pt": 5, "relation": "opposite", "description": "表裏一体な最高の相性◎"},
        "ISFJ": {"pt": 4, "relation": "active", "description": "居心地が良く気持ちがプラスになる"},
        "ENTJ": {"pt": 3, "relation": "mirror", "description": "心理は似てて態度が違う双子みたい"},
        "ISTP": {"pt": 3, "relation": "similler", "description": "ビジネスライクな似た者同士"},
        "ESTP": {"pt": 2, "relation": "opposite_sub", "description": "惹かれ合いゆっくり距離が縮まる"},
        "ENFP": {"pt": 2, "relation": "relax", "description": "ダラダラ快適で温かく安定感あり"},
        "INTP": {"pt": 1, "relation": "same", "description": "理解し合えるが助け合いが難しい"},
        "INTJ": {"pt": 1, "relation": "same_sub", "description": "似てるようで似てない波ある関係"},
    },
    "ENTJ": {
        "ISFJ": {"pt": 5, "relation": "opposite", "description": "表裏一体な最高の相性◎"},
        "ESFP": {"pt": 4, "relation": "active", "description": "居心地が良く気持ちがプラスになる"},
        "INTP": {"pt": 3, "relation": "mirror", "description": "心理は似てて態度が違う双子みたい"},
        "ENFJ": {"pt": 3, "relation": "similler", "description": "ビジネスライクな似た者同士"},
        "INFJ": {"pt": 2, "relation": "opposite_sub", "description": "惹かれ合いゆっくり距離が縮まる"},
        "ISTJ": {"pt": 2, "relation": "relax", "description": "ダラダラ快適で温かく安定感あり"},
        "ENTJ": {"pt": 1, "relation": "same", "description": "理解し合えるが助け合いが難しい"},
        "ENTP": {"pt": 1, "relation": "same_sub", "description": "似てるようで似てない波ある関係"},
    },
    "ENTP": {
        "ISFP": {"pt": 5, "relation": "opposite", "description": "表裏一体な最高の相性◎"},
        "ESFJ": {"pt": 4, "relation": "active", "description": "居心地が良く気持ちがプラスになる"},
        "INTJ": {"pt": 3, "relation": "mirror", "description": "心理は似てて態度が違う双子みたい"},
        "ESTP": {"pt": 3, "relation": "similler", "description": "ビジネスライクな似た者同士"},
        "ISTP": {"pt": 2, "relation": "opposite_sub", "description": "惹かれ合いゆっくり距離が縮まる"},
        "INFP": {"pt": 2, "relation": "relax", "description": "ダラダラ快適で温かく安定感あり"},
        "ENTP": {"pt": 1, "relation": "same", "description": "理解し合えるが助け合いが難しい"},
        "ENTJ": {"pt": 1, "relation": "same_sub", "description": "似てるようで似てない波ある関係"},
    },
    "INFJ": {
        "ESTJ": {"pt": 5, "relation": "opposite", "description": "表裏一体な最高の相性◎"},
        "ISTP": {"pt": 4, "relation": "active", "description": "居心地が良く気持ちがプラスになる"},
        "ENFP": {"pt": 3, "relation": "mirror", "description": "心理は似てて態度が違う双子みたい"},
        "INTJ": {"pt": 3, "relation": "similler", "description": "ビジネスライクな似た者同士"},
        "ENTJ": {"pt": 2, "relation": "opposite_sub", "description": "惹かれ合いゆっくり距離が縮まる"},
        "ESFJ": {"pt": 2, "relation": "relax", "description": "ダラダラ快適で温かく安定感あり"},
        "INFJ": {"pt": 1, "relation": "same", "description": "理解し合えるが助け合いが難しい"},
        "INFP": {"pt": 1, "relation": "same_sub", "description": "似てるようで似てない波ある関係"},
    },
    "ENFJ": {
        "ISTJ": {"pt": 5, "relation": "opposite", "description": "表裏一体な最高の相性◎"},
        "ESTP": {"pt": 4, "relation": "active", "description": "居心地が良く気持ちがプラスになる"},
        "INFP": {"pt": 3, "relation": "mirror", "description": "心理は似てて態度が違う双子みたい"},
        "ENTJ": {"pt": 3, "relation": "similler", "description": "ビジネスライクな似た者同士"},
        "INTJ": {"pt": 2, "relation": "opposite_sub", "description": "惹かれ合いゆっくり距離が縮まる"},
        "ISFJ": {"pt": 2, "relation": "relax", "description": "ダラダラ快適で温かく安定感あり"},
        "ENFJ": {"pt": 1, "relation": "same", "description": "理解し合えるが助け合いが難しい"},
        "ENFP": {"pt": 1, "relation": "same_sub", "description": "似てるようで似てない波ある関係"},
    },
    "INFP": {
        "ESTP": {"pt": 5, "relation": "opposite", "description": "表裏一体な最高の相性◎"},
        "ISTJ": {"pt": 4, "relation": "active", "description": "居心地が良く気持ちがプラスになる"},
        "ENFJ": {"pt": 3, "relation": "mirror", "description": "心理は似てて態度が違う双子みたい"},
        "ISFP": {"pt": 3, "relation": "similler", "description": "ビジネスライクな似た者同士"},
        "ESFP": {"pt": 2, "relation": "opposite_sub", "description": "惹かれ合いゆっくり距離が縮まる"},
        "ENTP": {"pt": 2, "relation": "relax", "description": "ダラダラ快適で温かく安定感あり"},
        "INFP": {"pt": 1, "relation": "same", "description": "理解し合えるが助け合いが難しい"},
        "INFJ": {"pt": 1, "relation": "same_sub", "description": "似てるようで似てない波ある関係"},
    },
    "ENFP": {
        "ISTP": {"pt": 5, "relation": "opposite", "description": "表裏一体な最高の相性◎"},
        "ESTJ": {"pt": 4, "relation": "active", "description": "居心地が良く気持ちがプラスになる"},
        "INFJ": {"pt": 3, "relation": "mirror", "description": "心理は似てて態度が違う双子みたい"},
        "ESFP": {"pt": 3, "relation": "similler", "description": "ビジネスライクな似た者同士"},
        "ISFP": {"pt": 2, "relation": "opposite_sub", "description": "惹かれ合いゆっくり距離が縮まる"},
        "INTP": {"pt": 2, "relation": "relax", "description": "ダラダラ快適で温かく安定感あり"},
        "ENFP": {"pt": 1, "relation": "same", "description": "理解し合えるが助け合いが難しい"},
        "ENFJ": {"pt": 1, "relation": "same_sub", "description": "似てるようで似てない波ある関係"},
    },
    "ISTJ": {
        "ENFJ": {"pt": 5, "relation": "opposite", "description": "表裏一体な最高の相性◎"},
        "INFP": {"pt": 4, "relation": "active", "description": "居心地が良く気持ちがプラスになる"},
        "ESTP": {"pt": 3, "relation": "mirror", "description": "心理は似てて態度が違う双子みたい"},
        "ISFJ": {"pt": 3, "relation": "similler", "description": "ビジネスライクな似た者同士"},
        "ESFJ": {"pt": 2, "relation": "opposite_sub", "description": "惹かれ合いゆっくり距離が縮まる"},
        "ENTJ": {"pt": 2, "relation": "relax", "description": "ダラダラ快適で温かく安定感あり"},
        "ISTJ": {"pt": 1, "relation": "same", "description": "理解し合えるが助け合いが難しい"},
        "ISTP": {"pt": 1, "relation": "same_sub", "description": "似てるようで似てない波ある関係"},
    },
    "ISFJ": {
        "ENTJ": {"pt": 5, "relation": "opposite", "description": "表裏一体な最高の相性◎"},
        "INTP": {"pt": 4, "relation": "active", "description": "居心地が良く気持ちがプラスになる"},
        "ESFP": {"pt": 3, "relation": "mirror", "description": "心理は似てて態度が違う双子みたい"},
        "ISTJ": {"pt": 3, "relation": "similler", "description": "ビジネスライクな似た者同士"},
        "ESTJ": {"pt": 2, "relation": "opposite_sub", "description": "惹かれ合いゆっくり距離が縮まる"},
        "ENFJ": {"pt": 2, "relation": "relax", "description": "ダラダラ快適で温かく安定感あり"},
        "ISFJ": {"pt": 1, "relation": "same", "description": "理解し合えるが助け合いが難しい"},
        "ISFP": {"pt": 1, "relation": "same_sub", "description": "似てるようで似てない波ある関係"},
    },
    "ESTJ": {
        "INFJ": {"pt": 5, "relation": "opposite", "description": "表裏一体な最高の相性◎"},
        "ENFP": {"pt": 4, "relation": "active", "description": "居心地が良く気持ちがプラスになる"},
        "ISTP": {"pt": 3, "relation": "mirror", "description": "心理は似てて態度が違う双子みたい"},
        "ESFJ": {"pt": 3, "relation": "similler", "description": "ビジネスライクな似た者同士"},
        "ISFJ": {"pt": 2, "relation": "opposite_sub", "description": "惹かれ合いゆっくり距離が縮まる"},
        "INTJ": {"pt": 2, "relation": "relax", "description": "ダラダラ快適で温かく安定感あり"},
        "ESTJ": {"pt": 1, "relation": "same", "description": "理解し合えるが助け合いが難しい"},
        "ESTP": {"pt": 1, "relation": "same_sub", "description": "似てるようで似てない波ある関係"},
    },
    "ESFJ": {
        "INTJ": {"pt": 5, "relation": "opposite", "description": "表裏一体な最高の相性◎"},
        "ENTP": {"pt": 4, "relation": "active", "description": "居心地が良く気持ちがプラスになる"},
        "ISFP": {"pt": 3, "relation": "mirror", "description": "心理は似てて態度が違う双子みたい"},
        "ESTJ": {"pt": 3, "relation": "similler", "description": "ビジネスライクな似た者同士"},
        "ISTJ": {"pt": 2, "relation": "opposite_sub", "description": "惹かれ合いゆっくり距離が縮まる"},
        "INFJ": {"pt": 2, "relation": "relax", "description": "ダラダラ快適で温かく安定感あり"},
        "ESFJ": {"pt": 1, "relation": "same", "description": "理解し合えるが助け合いが難しい"},
        "ESFP": {"pt": 1, "relation": "same_sub", "description": "似てるようで似てない波ある関係"},
    },
    "ESTP": {
        "INFP": {"pt": 5, "relation": "opposite", "description": "表裏一体な最高の相性◎"},
        "ENFJ": {"pt": 4, "relation": "active", "description": "居心地が良く気持ちがプラスになる"},
        "ISTJ": {"pt": 3, "relation": "mirror", "description": "心理は似てて態度が違う双子みたい"},
        "ENTP": {"pt": 3, "relation": "similler", "description": "ビジネスライクな似た者同士"},
        "INTP": {"pt": 2, "relation": "opposite_sub", "description": "惹かれ合いゆっくり距離が縮まる"},
        "ISFP": {"pt": 2, "relation": "relax", "description": "ダラダラ快適で温かく安定感あり"},
        "ESTP": {"pt": 1, "relation": "same", "description": "理解し合えるが助け合いが難しい"},
        "ESTJ": {"pt": 1, "relation": "same_sub", "description": "似てるようで似てない波ある関係"},
    },
    "ISTP": {
        "ENFP": {"pt": 5, "relation": "opposite", "description": "表裏一体な最高の相性◎"},
        "INFJ": {"pt": 4, "relation": "active", "description": "居心地が良く気持ちがプラスになる"},
        "ESTJ": {"pt": 3, "relation": "mirror", "description": "心理は似てて態度が違う双子みたい"},
        "INTP": {"pt": 3, "relation": "similler", "description": "ビジネスライクな似た者同士"},
        "ENTP": {"pt": 2, "relation": "opposite_sub", "description": "惹かれ合いゆっくり距離が縮まる"},
        "ESFP": {"pt": 2, "relation": "relax", "description": "ダラダラ快適で温かく安定感あり"},
        "ISTP": {"pt": 1, "relation": "same", "description": "理解し合えるが助け合いが難しい"},
        "ISTJ": {"pt": 1, "relation": "same_sub", "description": "似てるようで似てない波ある関係"},
    },
    "ISFP": {
        "ENTP": {"pt": 5, "relation": "opposite", "description": "表裏一体な最高の相性◎"},
        "INTJ": {"pt": 4, "relation": "active", "description": "居心地が良く気持ちがプラスになる"},
        "ESFJ": {"pt": 3, "relation": "mirror", "description": "心理は似てて態度が違う双子みたい"},
        "INFP": {"pt": 3, "relation": "similler", "description": "ビジネスライクな似た者同士"},
        "ENFP": {"pt": 2, "relation": "opposite_sub", "description": "惹かれ合いゆっくり距離が縮まる"},
        "ESTP": {"pt": 2, "relation": "relax", "description": "ダラダラ快適で温かく安定感あり"},
        "ISFP": {"pt": 1, "relation": "same", "description": "理解し合えるが助け合いが難しい"},
        "ISFJ": {"pt": 1, "relation": "same_sub", "description": "似てるようで似てない波ある関係"},
    },
    "ESFP": {
        "INTP": {"pt": 5, "relation": "opposite", "description": "表裏一体な最高の相性◎"},
        "ENTJ": {"pt": 4, "relation": "active", "description": "居心地が良く気持ちがプラスになる"},
        "ISFJ": {"pt": 3, "relation": "mirror", "description": "心理は似てて態度が違う双子みたい"},
        "ENFP": {"pt": 3, "relation": "similler", "description": "ビジネスライクな似た者同士"},
        "INFP": {"pt": 2, "relation": "opposite_sub", "description": "惹かれ合いゆっくり距離が縮まる"},
        "ISTP": {"pt": 2, "relation": "relax", "description": "ダラダラ快適で温かく安定感あり"},
        "ESFP": {"pt": 1, "relation": "same", "description": "理解し合えるが助け合いが難しい"},
        "ESFJ": {"pt": 1, "relation": "same_sub", "description": "似てるようで似てない波ある関係"},
    },
    # 他のMBTIタイプも同様に記述
}

def get_mbti_compatibility(user_mbti, profile_mbti):
    """
    ユーザーのMBTIを基準に、プロフィールのMBTIとの相性スコアと関係名称を取得
    """
    compatibility = mbti_matrix.get(user_mbti, {}).get(profile_mbti, {"pt": 0, "name": "不明"})
    return compatibility  # {"pt": 5, "name": "双対関係"} のような辞書を返す

# MBTIベースの詳細説明画面への誘導URL
mbti_links = {
    "INTJ": "https://www.16personalities.com/ja/intj%E5%9E%8B%E3%81%AE%E6%80%A7%E6%A0%BC",
    "INTP": "https://www.16personalities.com/ja/intp%E5%9E%8B%E3%81%AE%E6%80%A7%E6%A0%BC",
    "ENTJ": "https://www.16personalities.com/ja/entj%E5%9E%8B%E3%81%AE%E6%80%A7%E6%A0%BC",
    "ENTP": "https://www.16personalities.com/ja/entp%E5%9E%8B%E3%81%AE%E6%80%A7%E6%A0%BC",
    "INFJ": "https://www.16personalities.com/ja/infj%E5%9E%8B%E3%81%AE%E6%80%A7%E6%A0%BC",
    "INFP": "https://www.16personalities.com/ja/infp%E5%9E%8B%E3%81%AE%E6%80%A7%E6%A0%BC",
    "ENFJ": "https://www.16personalities.com/ja/enfj%E5%9E%8B%E3%81%AE%E6%80%A7%E6%A0%BC",
    "ENFP": "https://www.16personalities.com/ja/enfp%E5%9E%8B%E3%81%AE%E6%80%A7%E6%A0%BC",
    "ISTJ": "https://www.16personalities.com/ja/istj%E5%9E%8B%E3%81%AE%E6%80%A7%E6%A0%BC",
    "ISFJ": "https://www.16personalities.com/ja/isfj%E5%9E%8B%E3%81%AE%E6%80%A7%E6%A0%BC",
    "ESTJ": "https://www.16personalities.com/ja/estj%E5%9E%8B%E3%81%AE%E6%80%A7%E6%A0%BC",
    "ESFJ": "https://www.16personalities.com/ja/esfj%E5%9E%8B%E3%81%AE%E6%80%A7%E6%A0%BC",
    "ISTP": "https://www.16personalities.com/ja/istp%E5%9E%8B%E3%81%AE%E6%80%A7%E6%A0%BC",
    "ISFP": "https://www.16personalities.com/ja/isfp%E5%9E%8B%E3%81%AE%E6%80%A7%E6%A0%BC",
    "ESTP": "https://www.16personalities.com/ja/estp%E5%9E%8B%E3%81%AE%E6%80%A7%E6%A0%BC",
    "ESFP": "https://www.16personalities.com/ja/esfp%E5%9E%8B%E3%81%AE%E6%80%A7%E6%A0%BC",
}

def get_mbti_detail_url(mbti):
    """
    MBTIから該当詳細説明URLを取得
    """
    return mbti_links.get(mbti, []) # mbtiに該当するURLを返す
