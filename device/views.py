import os
from django.utils.timezone import now
import logging
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Device
from .forms  import DeviceForm

# ロガー取得
logger = logging.getLogger('app')
error_logger = logging.getLogger('error')

def list_view(request, page_cnt=1):
    logger.debug('start Device list_view')

    page_size = 12 # disply page size
    onEachSide = 2 # display how many pages around current page
    onEnds = 2 # display how many pages on first/last edge
 
    try:
        page_cnt = int(request.GET.get("page_cnt", 1))
    except ValueError:
        logger.debug('couldnt catch the page cnt')
        page_cnt = 1
    
    object_list = Device.objects.order_by('-id').all() 

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

    logger.info('return render device/list.html')
    return render(request, 'device/list.html', context)


def detail_view(request, pk):
    logger.info('start Device detail_view')

    logger.debug('get Device object(pk)')
    object = get_object_or_404(Device, pk=pk)

    context = {'object': object}

    logger.debug('return render device/detail.html')
    return render(request, 'device/detail.html', context)


@login_required
def create_view(request):
    logger.info('start Device create_view')

    if request.method == "POST":
        logger.info('POST method')

        form = DeviceForm(request.POST, request.FILES)
        context = {'form': form}

        if form.is_valid():
            logger.debug('Device form.is_valid')

            name_data = form.cleaned_data['name']

            images_data = request.FILES.get("images")
            themes_data = request.FILES.get("themes")

            maker_data = form.cleaned_data['maker']
            productno_data = form.cleaned_data['productno']
            context_data = form.cleaned_data['context']
            remarks_data = form.cleaned_data['remarks']

            try:
                object = Device.objects.create(
                    name = name_data,
                    images = None, # 画像はまだ保存しない
                    themes = None, # 画像はまだ保存しない
                    maker = maker_data,
                    productno = productno_data,
                    context = context_data,
                    remarks = remarks_data,
                )
            except Exception as e:
                logger.error(f'couldnt create the Device object: {e}')
                logger.info('return render device/create.html')
                return render(request, 'device/create.html', {'form': form})

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
                    logger.error(f'couldnt save the images_data / themes_data in Device object: {e}')
            
            logger.info('return redirect device:list')
            return redirect('device:list')
        else:
            logger.error('form is invalid.')
            print(form.errors)  # エラー内容をログに出力
    else:
        logger.info('GET method')
        form = DeviceForm()
        context = {'form': form}
    
    logger.info('return render device/create.html')
    return render(request, 'device/create.html', context)
    

@login_required
def update_view(request, pk):
    logger.info('start Device update_view')

    logger.debug('get Device object(pk)')
    object = get_object_or_404(Device, pk=pk)
    
    if request.method == "POST":
        logger.info('POST method')

        form = DeviceForm(request.POST, request.FILES)
        context = {'object': object, 'form': form}

        if form.is_valid():
            logger.debug('form.is_valid')

            object.name = form.cleaned_data['name']
            object.maker = form.cleaned_data['maker']
            object.productno = form.cleaned_data['productno']
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
                logger.debug('save updated Device object')
                object.save()
            except Exception as e:
                logger.error(f'couldnt save the Device object: {e}')

            logger.info('return redirect device:list')
            return redirect('device:list')
        else:
            logger.error('form not is_valid.')
            print(form.errors)  # エラー内容をログに出力
    else:
        logger.info('GET method')
        form = DeviceForm(instance=object) # putback the form
        context = {'object': object, 'form': form}
    
    logger.info('return render device/update.html')
    return render(request, 'device/update.html', context)


@login_required
def delete_view(request, pk):
    logger.info('start Device delete_view')

    logger.debug('get Device object(pk)')
    object = get_object_or_404(Device, pk=pk)
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
            logger.debug('delete old Device object')
            object.delete()
        except Exception as e:
            logger.error(f'couldnt delete Device object: {e}')

        logger.info('return redirect device:list')
        return redirect('device:list')
    else:
        logger.info('GET method')
    
    logger.info('return render device/delete.html')
    return render(request, 'device/delete.html', context)

@csrf_exempt  # 関数デコレータに変更
@login_required
def push_likes(request, pk):
    logger.info('start Device push_likes')

    if request.method == 'POST':
        logger.info('POST method')

        device = get_object_or_404(Device, id=pk)
        logger.debug(f'get Device object(pk)={device}')

        # いいね処理を実行
        device.push_likes(request)

        # Ajaxにいいね数を返す
        logger.info(f'return likes:({device.likes})')
        return JsonResponse({'likes': f'({device.likes})'})

    logger.info(f'return Invalid request:status=400')
    return JsonResponse({'error': 'Invalid request'}, status=400)
