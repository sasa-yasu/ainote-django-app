import math
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import logging

# ロガー取得
logger = logging.getLogger('app')
error_logger = logging.getLogger('error')

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


def haversine(lat1, lon1, lat2, lon2):
    """2点間のハーサイン距離から近くにいるかを判断"""
    R = 6371  # 地球の半径（キロメートル）
    tolerance = 0.3  # 300メートル範囲

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
