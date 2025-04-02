import os
import qrcode
from io import BytesIO
from PIL import Image
from django.conf import settings
from django.utils.timezone import now
import logging
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Group
from .forms  import GroupForm
from user.models import Profile

# ロガー取得
logger = logging.getLogger('app')
error_logger = logging.getLogger('error')

def list_view(request, page_cnt=1):
    logger.debug('start Group list_view')

    page_size = 12 # disply page size
    onEachSide = 2 # display how many pages around current page
    onEnds = 2 # display how many pages on first/last edge
 
    try:
        page_cnt = int(request.GET.get("page_cnt", 1))
    except ValueError:
        logger.debug('couldnt catch the page cnt')
        page_cnt = 1
    
    object_list = Group.objects.order_by('-id').all() 

    if object_list.exists():
        logger.debug('object_list exists')
        paginator = Paginator(object_list, page_size)
        try:
            display_object_list = paginator.page(page_cnt)
        except:
            logger.warning('couldnt catch the display_object_list page_cnt=', page_cnt)
            display_object_list = paginator.page(1)        
        link_object_list = display_object_list.paginator.get_elided_page_range(
            page_cnt, on_each_side=onEachSide, on_ends=onEnds
        )
    else:
        logger.debug('object_list not exists')
        display_object_list = []
        link_object_list = []

    context = {'display_object_list': display_object_list, 'link_object_list': link_object_list}

    logger.info('return render group/list.html')
    return render(request, 'group/list.html', context)


def detail_view(request, pk):
    logger.info('start Group detail_view')

    logger.debug('get Group object(pk)')
    object = get_object_or_404(Group, pk=pk)

    # 所属しているすべてのグループを取得
    joined_profiles = object.get_profiles

    context = {'object': object, 'joined_profiles': joined_profiles}

    logger.debug('return render group/detail.html')
    return render(request, 'group/detail.html', context)


@login_required
def create_view(request):
    logger.info('start Group create_view')

    if request.method == "POST":
        logger.info('POST method')

        form = GroupForm(request.POST, request.FILES)
        context = {'form': form}

        if form.is_valid():
            logger.debug('Group form.is_valid')

            name_data = form.cleaned_data['name']

            images_data = request.FILES.get("images")
            themes_data = request.FILES.get('themes')
            
            context_data = form.cleaned_data['context']
            remarks_data = form.cleaned_data['remarks']

            try:
                object = Group.objects.create(
                    name = name_data,
                    images = None, # 画像はまだ保存しない
                    themes = None, # 画像はまだ保存しない
                    context = context_data,
                    remarks = remarks_data,
                )
            except Exception as e:
                logger.error(f'couldnt create the Group object: {e}')
                logger.info('return render group/create.html')
                return render(request, 'group/create.html', {'form': form})

            if images_data or themes_data:
                if images_data:
                    logger.debug('images_data exists')
                    ext = os.path.splitext(images_data.name)[1]  # 拡張子を取得
                    timestamp = now().strftime('%y%m%d%H%M')  # タイムスタンプ生成 (yyMMddHHmm)
                    images_data.name = f"{object.id}_images_{timestamp}{ext}"  # 例: "12_2503201935.jpg"
                    logger.debug(f'images_data={images_data}')
                    object.images = images_data

                if themes_data:
                    logger.debug('themes_data exists')
                    ext = os.path.splitext(themes_data.name)[1]  # 拡張子を取得
                    timestamp = now().strftime('%y%m%d%H%M')  # タイムスタンプ生成 (yyMMddHHmm)
                    themes_data.name = f"{object.id}_themes_{timestamp}{ext}"  # 例: "12_2503201935.jpg"
                    logger.debug(f'themes_data={themes_data}')
                    object.themes = themes_data

                try:
                    object.save()
                except Exception as e:
                    logger.error(f'couldnt save the images_data / themes_data in Group object: {e}')

            logger.info('return redirect group:list')
            return redirect('group:list')
        else:
            logger.error('form is invalid.')
            print(form.errors)  # エラー内容をログに出力
    else:
        logger.info('GET method')
        form = GroupForm()
        context = {'form': form}
    
    logger.info('return render group/create.html')
    return render(request, 'group/create.html', context)
    

@login_required
def update_view(request, pk):
    logger.info('start Group update_view')

    logger.debug('get Group object(pk)')
    object = get_object_or_404(Group, pk=pk)
    
    if request.method == "POST":
        logger.info('POST method')

        form = GroupForm(request.POST, request.FILES)
        context = {'object': object, 'form': form}

        if form.is_valid():
            logger.debug('form.is_valid')

            object.name = form.cleaned_data['name']
            object.context = form.cleaned_data['context']
            object.remarks = form.cleaned_data['remarks']

            images_data = request.FILES.get("images")
            themes_data = request.FILES.get('themes')

            if images_data or themes_data:
                if images_data: # File Selected
                    logger.debug('images_data exists')

                    # **古いファイルを削除**
                    if object.images:
                        logger.debug('old images_data exists')
                        old_image_path = object.images.path  # 旧ファイルのパス
                        logger.debug(f'old images_data={old_image_path}')
                        if default_storage.exists(old_image_path):
                            logger.debug('old images_data file exists')
                            try:
                                logger.debug('delete old images_data')
                                default_storage.delete(old_image_path)  # 削除
                            except Exception as e:
                                logger.error(f'couldnt delete old images_data={old_image_path}: {e}')
                        else:
                            logger.debug('old images_data file not exists')
                    # **新しいファイルを保存**
                    ext = os.path.splitext(images_data.name)[1]  # 拡張子を取得
                    timestamp = now().strftime('%y%m%d%H%M')  # タイムスタンプ生成 (yyMMddHHmm)
                    images_data.name = f"{object.id}_images_{timestamp}{ext}"  # 例: "12_2503201935.jpg"
                    logger.debug(f'new images_data={images_data}')
                    logger.debug('save new images_data')
                    object.images = images_data


                if themes_data: # File Selected
                    logger.debug(f'themes_data exists={themes_data}')
                    # **古いファイルを削除**
                    if object.themes:
                        logger.debug('old themes_data exists')
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
                    # **新しいファイルを保存**
                    ext = os.path.splitext(themes_data.name)[1]  # 拡張子を取得
                    timestamp = now().strftime('%y%m%d%H%M')  # タイムスタンプ生成 (yyMMddHHmm)
                    themes_data.name = f"{object.id}_themes_{timestamp}{ext}"  # 例: "12_2503201935.jpg"
                    logger.debug(f'new themes_data={themes_data}')
                    logger.debug('save new themes_data')
                    object.themes = themes_data

            try:
                logger.debug('save updated Group object')
                object.save()
            except Exception as e:
                logger.error(f'couldnt save the Group object: {e}')

            logger.info('return redirect group:list')
            return redirect('group:list')
        else:
            logger.error('form not is_valid.')
            print(form.errors)  # エラー内容をログに出力
    else:
        logger.info('GET method')
        form = GroupForm(instance=object) # putback the form
        context = {'object': object, 'form': form}
    
    logger.info('return render group/update.html')
    return render(request, 'group/update.html', context)


@login_required
def delete_view(request, pk):
    logger.info('start Group delete_view')

    logger.debug('get Group object(pk)')
    object = get_object_or_404(Group, pk=pk)
    context = {'object': object}

    if request.method == "POST":
        logger.info('POST method')

        # **古いファイルを削除**
        if object.images:
            logger.debug('old images_data exists')
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

        # **古いファイルを削除**
        if object.themes:
            logger.debug('old themes_data exists')
            old_image_path = object.themes.path  # 旧ファイルのパス
            logger.debug(f'old themes_data={old_image_path}')
            if default_storage.exists(old_image_path):
                logger.debug('old themes_data file exists')
                try:
                    logger.debug('delete old themes_data')
                    default_storage.delete(old_image_path)  # 削除
                except Exception as e:
                    logger.debug(f'couldnt delete old themes_data={old_image_path}: {e}')
            else:
                logger.debug('old themes_data file not exists')

        try:
            logger.debug('delete old Group object')
            object.delete()
        except Exception as e:
            logger.error(f'couldnt delete Group object: {e}')

        logger.info('return redirect group:list')
        return redirect('group:list')
    else:
        logger.info('GET method')
    
    logger.info('return render group/delete.html')
    return render(request, 'group/delete.html', context)

@login_required
def disp_qr_view(request, group_id):
    logger.info('start Friend disp_qr_view')

    base_url = f"{settings.SITE_DOMAIN}/group/join/?group_id="  # 実際のドメインに要変更
    group_url = f"{base_url}{group_id}"
    logger.info(f'group_url={ group_url }')
    
    qr = qrcode.QRCode(
        version=4,  # サイズ (1～40, 数字が大きいほどサイズが大きい)
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # エラーレベル
        box_size=10,  # 1セルあたりのピクセルサイズ
        border=6,  # ボーダーサイズ
    )
    
    qr.add_data(group_url) # create QR code
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

@login_required
def join_view(request):
    logger.info('start Group join_view')

    # profile_own = operator
    try:
        profile_own = Profile.objects.get(user1=request.user) # get login profile object
        logger.debug(f'profile_own={profile_own}')
    except Exception as e:
        logger.error(f'couldnt get my request.user={request.user}: {e}')
        profile_own = None

    # profile_with = friend target
    try:
        group_id = int(request.GET.get("group_id", 1)) # get profile_id from URL query
        logger.debug(f'group_id={group_id}')
        group_join = Group.objects.get(id=group_id)
    except ValueError:
        logger.debug(f'couldnt catch target group_id={group_id}')
        group_id = 1

    context = {'profile_own': profile_own, 'group_join': group_join}

    if request.method == "POST":
        logger.info('POST method')

        # GETの情報ではなく、POSTの情報から2つのProfileを取得(ACCEPTを押下されたもののみ)
        group_join_id = request.POST["group_join_id"]
        logger.debug(f'POST group_join_id={group_join_id}')
        group = get_object_or_404(Group, id=group_join_id)
        logger.debug(f'POST group={group}')

        try:
            # GroupにProfileを登録
            profile_own.groups.add(group)
            profile_own.save()
        except Exception as e:
            logger.error(f'couldnt create group-profile object group_id={group.id} profile_id={profile_own.id}: {e}')

        logger.info('return redirect user:list')
        return redirect('user:list')
    else:
        logger.info('GET method')
        pass

    logger.info('return render group/join.html')
    return render(request, 'group/join.html', context)

@csrf_exempt  # 関数デコレータに変更
@login_required
def push_likes(request, pk):
    logger.info('start Group push_likes')

    if request.method == 'POST':
        logger.info('POST method')

        group = get_object_or_404(Group, id=pk)
        logger.debug(f'get Group object(pk)={group}')

        # いいね処理を実行
        group.push_likes(request)

        # Ajaxにいいね数を返す
        logger.info(f'return likes:({group.likes})')
        return JsonResponse({'likes': f'({group.likes})'})

    logger.info(f'return Invalid request:status=400')
    return JsonResponse({'error': 'Invalid request'}, status=400)
